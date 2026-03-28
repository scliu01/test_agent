import json
import os
import re
import tempfile
import traceback
import uuid

from flask import Blueprint, request, Response
from openai import OpenAI

from HDT.models.projects import Project
from HDT.utils.ai_utils import parse_markdown, load_prompt
from HDT.utils.doc_utils import generate_image_uuid
from HDT.utils.resp_model import respModel
from app import app_server, database
from HDT.models.api_document import ApiDocument
from datetime import datetime

# 路由名称
module_name = "api_document"
# 路由对象，在app.py中加载到flask对象中
module_route = Blueprint(f"route_{module_name}", __name__)
# 数据库模块名称
module_model = ApiDocument


# 查询所有数据
@module_route.route(f"/{module_name}/queryAll", methods=["GET"])
def queryAll():
    project_id = request.args.get("project_id")
    print(f"查询项目下的数据模板:{project_id}")
    with app_server.app_context():
        query = module_model.query
        if project_id:
            query = query.filter_by(project_id=project_id)
        return respModel().ok_resp_list(lst=query.all(), msg="查询成功")


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


@module_route.route(f"/{module_name}/importDocument", methods=["POST"])
def import_document():
    # 文件验证部分保持不变
    if 'file' not in request.files:
        return respModel.error_resp(msg="请选择文件")

    file = request.files['file']
    if file.filename == '':
        return respModel.error_resp(msg="请选择文件")

    # 获取文件类型后缀
    file_extension = os.path.splitext(file.filename)[1]
    if not file.filename.lower().endswith('.docx') and not file.filename.lower().endswith('.md'):
        return respModel.error_resp(msg="文件格式错误")

    try:
        print("接收到的参数：", request.form)
        # 参数处理
        replace_existing = request.form.get('replace_existing', 'false').lower() == 'true'
        max_level = int(request.form.get('max_level', 3))
        project_id = int(request.form.get('project_id', None))

        # 清理现有数据（如果需要）
        if replace_existing:
            with app_server.app_context():
                print("正在清理需求对应的现有数据...")
                module_model.query.filter_by(project_id=project_id).delete()
                # 删除文件夹
                # shutil.rmtree(os.path.join(dev_settings.UPLOAD_FOLDER, str(project_id)), ignore_errors=True)
                # 提交事务
                database.session.commit()

        # 保存临时文件，用来保存文件
        temp_path = os.path.join(tempfile.gettempdir(), f"temp_{uuid.uuid4().hex}.{file_extension}")
        file.save(temp_path)

        if file_extension == '.docx':
            from markitdown import MarkItDown
            md = MarkItDown(enable_plugins=True)
            full_markdown_text = md.convert(temp_path, keep_data_uris=True).text_content
        else:
            with open(temp_path, 'r', encoding='utf-8') as f:
                full_markdown_text = f.read()

        headers_to_split_on = [
                                  ("#", "level-1"),
                                  ("##", "level-2"),
                                  ("###", "level-3"),
                                  ("####", "level-4"),
                                  ("#####", "level-5"),
                                  ("######", "level-6"),
                              ][:max_level]  # 根据 max_level 限制拆分的层级
        from langchain_text_splitters import MarkdownHeaderTextSplitter
        splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            return_each_line=False,
            strip_headers=False
        )
        md_splits = splitter.split_text(full_markdown_text)
        print(f"文档数量{len(md_splits)}")
        # 创建一个指定长度 初始为None 的列表
        parent_infos = [None] * (max_level - 1)

        with app_server.app_context():
            for i, md_split in enumerate(md_splits):
                metadata = md_split.metadata
                markdown_text = md_split.page_content
                text_content = generate_image_uuid(markdown_text)

                # 检查是否需要创建父级节点
                level_size = len(metadata)
                if level_size == 0:
                    continue

                # 处理父标题的数据
                for index in range(1, level_size):
                    level_key = "level-" + str(index)
                    if parent_infos[index - 1] is None or metadata[level_key] != parent_infos[
                        index - 1].name:  # 如果父级节点名称不一致，则创建新的父级节点
                        print(f"创建父级节点：{metadata[level_key]}")
                        parent_id = None
                        if index > 1:
                            parent_id = parent_infos[index - 1].id
                        data = module_model(**{
                            "id": None,
                            "project_id": project_id,
                            "name": metadata[level_key],
                            "parent_id": parent_id,
                            "content": text_content,  # 由你的业务来决定
                        }, created_at=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
                        database.session.add(data)
                        database.session.flush()

                        parent_infos[index - 1] = data
                        print(f"创建父节点成功，ID为：{data.id}")

                # 创建当前节点
                parent_id = None
                if len(parent_infos) > 0:
                    parent_id = parent_infos[level_size - 2].id
                data = module_model(**{
                    "id": None,
                    "project_id": project_id,
                    "name": metadata[f'level-{level_size}'],
                    "parent_id": parent_id,
                    "content": text_content,
                    "ai_suggest": "{}",
                }, created_at=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
                print(f" project_id: {project_id}")
                database.session.add(data)
                database.session.flush()
                # print(f"父节点信息为：{parent_infos[level_size-2]}")
                print(f"创建当前节点：{metadata[f'level-{level_size}']}")
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            # 不提交，数据是不会进行数据库中的
            database.session.commit()
        # 清理临时文件
        os.remove(temp_path)

        return respModel.ok_resp(msg=f"成功导入")

    except Exception as e:
        print(f"初始化导入失败：{e}")
        traceback.print_exc()
        with app_server.app_context():
            database.session.rollback()
        return respModel.error_resp(msg=f"初始化导入失败：{e}")


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
            primary_doc = module_model.query.filter_by(id=int(primary_content)).first()
            if not primary_doc:
                return respModel.error_resp(msg=f"需求内容不存在: {primary_content}")
            secondary_docs = []
            if second_content is not None and len(second_content) > 0:
                for id in second_content.split(','):
                    secondary_doc = module_model.query.filter_by(id=int(id)).first()
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
        ai_prompt = load_prompt("../prompts", "提示词-接口文档评审.txt", {
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
