import json
import re
import traceback
from datetime import datetime

from flask import Blueprint, request, Response
from openai import OpenAI

from HDT.models.projects import Project
from HDT.utils.ai_utils import load_prompt
from HDT.utils.resp_model import respModel
from app import app_server, database
from HDT.models.test_data_template import TestDataTemplate

# 路由名称
module_name = "test_data_template"
# 路由对象，在app.py中加载到flask对象中
module_route = Blueprint(f"route_{module_name}", __name__)
# 数据库模块名称
module_model = TestDataTemplate


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
            # request.json获取POST请求的JSON数据
            print(f"接收到数据:{request.json}")
            request.json["id"] = None  # ID自增长
            # 如果已经没有created_at，就添加默认时间
            if request.json.get("created_at") is None:
                request.json["created_at"] = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
            data = module_model(**request.json)
            # 保存到数据库中
            database.session.add(data)
            # 获取新增后的ID并返回
            database.session.flush()
            data_id = data.id
            # 提交之后，数据才会真正保存到数据库中
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
        print(f"接收到数据:{data_id}")
        with app_server.app_context():
            # 数据库查询
            data = module_model.query.filter_by(id=data_id).first()
        if data:
            return respModel().ok_resp(obj=data)
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
        print(f"接收到数据:{data_id}")
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


def convert_fields_to_string(fields_list):
    """
    将字段字典数组转换为指定格式的多行字符串
    :param fields_list: 字段列表，格式为 [{"name": "", "type": "", "description": ""}, ...]
    :return: 格式化后的多行字符串
    """
    # 初始化结果列表，用于拼接每一行内容
    result = []
    # 遍历字段列表，带序号
    for idx, field in enumerate(fields_list, start=1):
        # 提取字段属性（处理空值，避免KeyError）
        field_name = field.get("name", "")
        field_type = field.get("type", "")
        field_desc = field.get("description", "")

        # 按指定格式拼接当前字段的内容，注意缩进（和示例一致）
        field_str = (
            f"                {idx}. 字段名：{field_name}\n"
            f"                  - 类型：{field_type}\n"
            f"                  - 描述：{field_desc}"
        )
        result.append(field_str)

    # 拼接所有字段，换行分隔，前后保留空行（和示例格式一致）
    final_str = "\n".join(result)
    # 外层包裹空行，匹配示例的格式
    final_str = f"\n{final_str}\n            "

    return final_str


@module_route.route(f"/{module_name}/process_with_ai_stream", methods=["POST"])
def process_with_ai_stream():
    """ 使用AI处理生成测试数据 """
    try:
        # 打印接收的参数
        print(f"接收到的参数: {request.json}")
        # 获取请求参数
        data_format = request.json.get("format", "json")
        project_id = request.json.get("project_id")
        example_result = request.json.get("example_result")
        fields = request.json.get("fields")
        data_count = request.json.get("data_count", 10)
        language = request.json.get("language", "zh")
        # 转换fields为字符串格式
        fields_str = convert_fields_to_string(fields)
        # 打印转换后的fields_str
        print(f"转换后的fields_str: {fields_str}")

        result_format = f"""
                ```{data_format}

                ```
            """

        if not project_id:
            return respModel.error_resp(msg="缺少必填参数: project_id")

        # 根据project_id查询项目配置的AI模型地址
        with app_server.app_context():
            # 先从project表查询model字段
            project = Project.query.filter_by(id=project_id).first()
            if not project:
                return respModel.error_resp(msg=f"项目不存在: {project_id}")
            # 打印project
            print(f"项目: {str(project.to_dict())}")

            if not project.llm_url or not project.llm_key or not project.llm_model:
                return respModel.error_resp(msg=f"项目 {project_id} 未配置AI模型地址")

            ai_prompt = load_prompt("../prompts", "提示词-AI生成测试数据.txt", {
                "count": data_count,
                "data_format": data_format,
                "example_result": example_result,
                "fields": fields,
                "language": language,
                "result_format": result_format
            })
            print(f"生成的提示词: {ai_prompt}")
            # 使用OpenAI调用指定的大模型
            # 配置OpenAI客户端
            client = OpenAI(
                base_url=project.llm_url,
                # 注意：API密钥应通过环境变量或安全方式设置
                api_key=project.llm_key
            )
            # 调用大模型（流式）
            stream = client.chat.completions.create(
                model=project.llm_model,
                messages=[{"role": "user", "content": ai_prompt}],
                stream=True
            )

            # 设置流式响应
            def generate():
                try:
                    # 发送初始消息，yield将内容返回给前端, status是状态，start是开始状态，自定义设计
                    yield json.dumps({"status": "start", "content": "开始生成内容"}) + "\n"

                    full_content = ""
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            content = chunk.choices[0].delta.content
                            full_content += content
                            # 发送流式数据，yield将内容返回给前端
                            yield json.dumps({
                                "status": "streaming",  # streaming表示流式数据
                                "content": content,
                                "full_content": full_content
                            }) + "\n"

                    # 尝试解析JSON
                    try:
                        if data_format == "json":
                            json_data = re.search(r"```json(.*?)```", full_content, re.DOTALL)
                            if json_data:
                                json_content = json_data.group(1)
                                parsed_data = json.loads(json_content)
                                yield json.dumps({
                                    "status": "completed",  # completed表示完成
                                    "data": parsed_data,
                                    "raw_content": full_content
                                }) + "\n"
                            else:
                                yield json.dumps({
                                    "status": "error",  # error表示错误
                                    "message": "未找到JSON格式数据",
                                    "raw_content": full_content
                                }) + "\n"
                        elif data_format == "sql":
                            sql_data = re.search(r"```sql(.*?)```", full_content, re.DOTALL)
                            if sql_data:
                                sql_content = sql_data.group(1)
                                yield json.dumps({
                                    "status": "completed",  # completed表示完成
                                    "data": sql_content,
                                    "raw_content": full_content
                                }) + "\n"
                            else:
                                yield json.dumps({
                                    "status": "error",  # error表示错误
                                    "message": "未找到SQL格式数据",
                                })

                    except json.JSONDecodeError as e:
                        yield json.dumps({
                            "status": "error",  # error表示错误
                            "message": f"JSON解析错误: {str(e)}",
                            "raw_content": full_content
                        }) + "\n"

                except Exception as e:
                    yield json.dumps({
                        "status": "error",  # error表示错误
                        "message": f"流式处理失败: {str(e)}"
                    }) + "\n"

            # 返回流式响应，需要导入 from flask import Response
            return Response(generate(), mimetype='text/plain', headers={'X-Accel-Buffering': 'no'})  # 禁用Nginx缓冲

    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(msg=f"AI处理失败: {str(e)}")
