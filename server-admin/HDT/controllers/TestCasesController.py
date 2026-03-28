import io
import json
import re
import traceback

import pandas as pd
from flask import Blueprint, request, Response, send_file
from openai import OpenAI

from HDT.models.projects import Project
from HDT.utils.ai_utils import parse_markdown, load_prompt
from HDT.utils.resp_model import respModel
from app import app_server, database
from HDT.models.test_case import TestCase
from HDT.models.document import Document
from datetime import datetime

# 路由名称
module_name = "test_case"
# 路由对象，在app.py中加载到flask对象中
module_route = Blueprint(f"route_{module_name}", __name__)
# 数据库模块名称
module_model = TestCase


# 查询所有数据
@module_route.route(f"/{module_name}/queryAll", methods=["GET"])
def queryAll():
    project_id = request.args.get("project_id")
    module_id = request.args.get("module_id")
    print(f"查询项目下的数据模板:{request.args}")
    with app_server.app_context():
        # 构建查询条件
        filter_list = []  # 保存查询结果
        if project_id:
            filter_list.append(module_model.project_id == project_id)
        if module_id:
            filter_list.append(module_model.module_id == module_id)

        # 执行查询
        if filter_list:
            datas = module_model.query.filter(*filter_list).all()
        else:
            datas = module_model.query.all()
        return respModel().ok_resp_list(lst=datas, msg="查询成功")


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        print(f"接收到的参数：{request.json}")
        # 分页查询
        page = request.json.get("page", 1)
        page_size = request.json.get("pageSize", 10)
        project_id = request.json.get("project_id")
        module_id = request.json.get("module_id")
        name = request.json.get("name")
        priority = request.json.get("priority")
        module_ids = request.json.get("module_ids")

        # 确保page和page_size是整数类型
        try:
            page = int(page)
            page_size = int(page_size)
        except (ValueError, TypeError):
            page = 1
            page_size = 10

        with app_server.app_context():
            # 构建查询条件
            filter_list = []  # 保存查询结果
            if project_id:
                filter_list.append(module_model.project_id == project_id)
            if module_id:
                filter_list.append(module_model.module_id == module_id)
            if module_ids:
                filter_list.append(module_model.module_id.in_(module_ids))
            if name:
                filter_list.append(module_model.name.like(f"%{name}%"))
            if priority:
                filter_list.append(module_model.priority == priority)

            # 按条件来查询
            datas = module_model.query.filter(*filter_list).limit(page_size).offset((page - 1) * page_size).all()
            print("datas", datas)
            # 查询当前条件的数据总数
            total = module_model.query.filter(*filter_list).count()
            print(f"查询结果：{datas}")
            print(f"查询结果总数：{total}")

            return respModel().ok_resp_list(lst=datas, total=total, page=page, pageSize=page_size)
    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    """ 新增数据 """
    try:
        with app_server.app_context():
            print(f"接收到数据:{request.json}")
            request.json["id"] = None  # ID自增长
            # 如果已经没有created_at，就添加默认时间
            if request.json.get("created_at") is None:
                request.json["created_at"] = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
            data = module_model(**request.json)
            database.session.add(data)
            # 获取新增后的ID并返回
            database.session.flush()
            data_id = data.id
            database.session.commit()
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.route(f"/{module_name}/queryById", methods=["GET"])
def queryById():
    """ 查询数据(单条记录) """
    try:
        data_id = int(request.args.get("id"))
        with app_server.app_context():
            # 数据库查询
            data = module_model.query.filter_by(id=data_id).first()
        if data:
            return respModel().ok_resp(obj=data, msg="查询成功")
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    """ 修改数据 """
    try:
        with app_server.app_context():
            print(f"接收到数据:{request.json}")
            module_model.query.filter_by(id=request.json["id"]).update(request.json)
            database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")


@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
def delete():
    """ 删除数据 """
    try:
        data_id = int(request.args.get("id"))
        print(f"删除的id:{data_id}")
        with app_server.app_context():
            project = module_model.query.filter_by(id=data_id).first()
            if project:
                database.session.delete(project)
                database.session.commit()
                return respModel.ok_resp(msg="删除成功")
            else:
                return respModel.error_resp(msg="项目不存在")
    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(f"服务器错误,删除失败：{e}")


# 批量删除
@module_route.route(f"/{module_name}/deleteBatch", methods=["POST", "DELETE"])
def deleteBatch():
    """ 批量删除数据 """
    try:
        print("批量删除的ids", request.json)
        data_ids = request.json.get('ids')
        if data_ids is None:  # 不能是None
            return respModel.error_resp(msg="缺少必填参数: ids")
        if not isinstance(data_ids, list):  # 一定是一个列表
            return respModel.error_resp(msg="参数ids必须是列表类型")
        if not data_ids:  # 不能是空字符串, ""
            return respModel.error_resp(msg="参数ids不能为空")
        with app_server.app_context():
            module_model.query.filter(module_model.id.in_(data_ids)).delete()
            database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(f"服务器错误,删除失败：{e}")


@module_route.route(f"/{module_name}/insertBatch", methods=["POST"])
def insertBatch():
    """ 批量新增数据 """
    try:
        print(f"接收到批量数据:{request.json}")
        with app_server.app_context():
            # 获取请求中的数据列表
            data_list = request.json.get("data_list")

            # 参数验证
            if data_list is None:
                return respModel.error_resp(msg="缺少必填参数: data_list")
            if not isinstance(data_list, list):
                return respModel.error_resp(msg="参数data_list必须是列表类型")
            if not data_list:
                return respModel.error_resp(msg="参数data_list不能为空列表")

            # 处理每条数据，创建对象列表
            model_objects = []
            for item in data_list:
                # ID自增长
                item["id"] = None
                # 如果没有created_at，添加默认时间
                if item.get("created_at") is None:
                    item["created_at"] = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
                # 创建模型对象
                model_objects.append(module_model(**item))

            # 批量添加到数据库
            database.session.add_all(model_objects)
            # flush获取ID
            database.session.flush()
            # 获取所有插入后的ID
            created_ids = [obj.id for obj in model_objects]
            # 提交事务
            database.session.commit()

            return respModel.ok_resp(msg="批量添加成功",
                                     dic_t={"insert_count": len(model_objects), "created_ids": created_ids})
    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(msg=f"批量添加失败:{e}")


@module_route.route(f"/{module_name}/process_with_ai_stream", methods=["POST"])
def process_with_ai_stream():
    """ 使用AI处理生成测试数据 """
    try:
        # 获取请求参数
        primary_content = request.json.get("primary_content")  # 主需求内容
        second_content = request.json.get("second_content")  # 补充说明
        hint = request.json.get("hint")
        project_id = request.json.get("project_id")
        # 打印接收的参数
        print(
            f"接收到的参数: primary_content={primary_content}, second_content={second_content}, hint={hint}, project_id={project_id}")

        if not primary_content:
            return respModel.error_resp(msg="缺少必填参数: primary_content")

        if not project_id:
            return respModel.error_resp(msg="缺少必填参数: project_id")

        # 根据project_id查询项目配置的AI模型地址
        with app_server.app_context():
            # 先从project表查询model字段
            project = Project.query.filter_by(id=project_id).first()
            if not project:
                return respModel.error_resp(msg=f"项目不存在: {project_id}")

            if not project.llm_url or not project.llm_key or not project.llm_model or not project.lvm_url or not project.lvm_key or not project.lvm_model:
                return respModel.error_resp(msg=f"项目 {project.name} 未配置AI大模型")

            # 查询需求内容
            primary_doc = Document.query.filter_by(id=int(primary_content)).first()
            if not primary_doc:
                return respModel.error_resp(msg=f"需求内容不存在: {primary_content}")
            secondary_docs = []
            if second_content is not None and len(second_content) > 0:
                for id in second_content.split(','):
                    secondary_doc = Document.query.filter_by(id=int(id)).first()
                    if secondary_doc:
                        secondary_docs.append(secondary_doc)

        # 使用OpenAI调用指定的大模型
        # 配置OpenAI客户端
        client = OpenAI(base_url=project.llm_url, api_key=project.llm_key)

        # 加载图片处理提示词
        image_parse_prompt = load_prompt("../prompts", "提示词-需求图片AI解析.txt", {})
        print(f"生成的提示词: {image_parse_prompt}")
        # 将需求文档中的图片内容转换成文字描述
        primary_doc_content = parse_markdown(primary_doc.content, project.lvm_key, project.lvm_url, project.lvm_model,
                                             image_parse_prompt)
        # 将需求文档中的图片内容转换成文字描述
        secondary_contents = [
            parse_markdown(doc.content, project.lvm_key, project.lvm_url, project.lvm_model, image_parse_prompt) for doc
            in secondary_docs]

        # 加载需求评审提示词
        ai_prompt = load_prompt("../prompts", "提示词-UI测试用例生成.txt", {
            "primary_content": primary_doc_content,
            "second_content": "\n".join(secondary_contents),
            "hint": hint,
        })
        print(f"生成的提示词: {ai_prompt}")

        # 设置流式响应
        def generate():
            try:
                # 调用大模型（流式）
                stream = client.chat.completions.create(
                    model=project.llm_model,
                    messages=[{"role": "user", "content": ai_prompt}],
                    stream=True
                )

                # 发送初始消息
                yield json.dumps({"status": "start", "content": "开始生成内容"}) + "\n"

                full_content = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_content += content
                        # 发送流式数据
                        yield json.dumps({
                            "status": "streaming",
                            "content": content,
                            "full_content": full_content
                        }) + "\n"

                # 尝试解析JSON
                try:
                    json_data = re.search(r"```json(.*?)```", full_content, re.DOTALL)
                    if json_data:
                        json_content = json_data.group(1)
                        parsed_data = json.loads(json_content)
                        yield json.dumps({
                            "status": "completed",
                            "data": parsed_data,
                            "raw_content": full_content
                        }) + "\n"
                    else:
                        yield json.dumps({
                            "status": "error",
                            "message": "未找到JSON格式数据",
                            "raw_content": full_content
                        }) + "\n"
                except json.JSONDecodeError as e:
                    yield json.dumps({
                        "status": "error",
                        "message": f"JSON解析错误: {str(e)}",
                        "raw_content": full_content
                    }) + "\n"

            except Exception as e:
                yield json.dumps({
                    "status": "error",
                    "message": f"流式处理失败: {str(e)}"
                }) + "\n"

        # 返回流式响应
        return Response(generate(), mimetype='text/plain',
                        headers={'X-Accel-Buffering': 'no'})  # 禁用Nginx缓冲
    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(msg=f"AI处理失败: {str(e)}")


@module_route.route(f"/{module_name}/export_excel", methods=["POST"])
def export_excel():
    """ 导出数据到Excel """
    try:
        print(f"接收到导出参数: {request.json}")

        project_id = request.json.get('project_id')
        module_id = request.json.get('module_id')

        # project_id 是必填参数，验证类型
        if project_id is None:
            return respModel.error_resp(msg="缺少必填参数: project_id")

        # 2. 优化查询逻辑
        with app_server.app_context():
            # 构建查询条件
            filter_list = []  # 保存查询结果
            if project_id:
                filter_list.append(module_model.project_id == project_id)
            if module_id:
                filter_list.append(module_model.module_id == module_id)

            # 执行查询
            if filter_list:
                datas = module_model.query.filter(*filter_list).all()

            if not datas:
                return respModel.error_resp(msg="没有找到符合条件的数据")

            # 3. 优化数据处理和Excel导出
            output = io.BytesIO()

            # 转换数据为字典列表，过滤掉不需要的字段
            data_dicts = []
            for item in datas:
                item_dict = item.to_dict()
                data_dicts.append(item_dict)

            # 使用pandas创建DataFrame并导出Excel
            df = pd.DataFrame(data_dicts)

            # 优化Excel写入，设置更友好的选项
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='测试用例', freeze_panes=(1, 0))

            output.seek(0)

            # 4. 文件名称
            filename = 'export_excel_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.xlsx'

            # 5. 返回Excel文件，设置更合适的响应头
            return send_file(
                output,
                as_attachment=True,
                download_name=filename,
            )

    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(msg=f"导出数据失败: {str(e)}")
