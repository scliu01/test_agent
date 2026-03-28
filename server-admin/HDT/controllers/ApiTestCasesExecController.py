import asyncio
import io
import json
import re
import traceback

import pandas as pd
from flask import Blueprint, request, Response, send_file
from openai import OpenAI

from HDT.models.projects import Project
from HDT.utils import VarRender, json_utils
from HDT.utils.VarRender import refresh
from HDT.utils.ai_utils import parse_markdown, load_prompt
from HDT.utils.resp_model import respModel
from app import app_server, database
from HDT.models.api_test_case_exec import ApiTestCaseExec
from HDT.models.api_test_case import ApiTestCase
from datetime import datetime
import requests

# 路由名称
module_name = "api_test_case_exec"
# 路由对象，在app.py中加载到flask对象中
module_route = Blueprint(f"route_{module_name}", __name__)
# 数据库模块名称
module_model = ApiTestCaseExec


# 查询所有数据
@module_route.route(f"/{module_name}/queryAll", methods=["GET"])
def queryAll():
    project_id = request.args.get("project_id")
    print(f"查询项目下的数据模板:{request.args}")
    if not project_id:
        return respModel().error_resp(msg="项目ID不能为空")
    with app_server.app_context():
        # 构建查询条件
        filter_list = []  # 保存查询结果
        if project_id:
            filter_list.append(module_model.project_id == project_id)

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

        # 确保page和page_size是整数类型
        try:
            page = int(page)
            page_size = int(page_size)
        except (ValueError, TypeError):
            page = 1
            page_size = 10
        if not project_id:
            return respModel().error_resp(msg="项目ID不能为空")
        with app_server.app_context():
            # 构建查询条件
            filter_list = []  # 保存查询结果
            if project_id:
                filter_list.append(module_model.project_id == project_id)

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


@module_route.route(f"/{module_name}/queryById", methods=["GET"])
def queryById():
    """ 查询数据(单条记录) """
    try:
        print(f"接收到的参数：{request.args}")
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


@module_route.route(f"/{module_name}/prepared_task", methods=["POST"])
def prepared_task():
    """ 创建测试执行任务 """
    print(f"接收到的参数：{request.json}")
    # 解析用例，返回需要补充的参数
    case_ids = request.json.get("case_ids").split(",")
    try:
        with app_server.app_context():
            first_param = {"服务器地址": "", "登录凭据": ""}
            list_case_param = [{
                "case_id": 0,
                "case_name": "AI自动化系统配置参数",
                "case_param": first_param
            }]
            # 查询 TestCase 表
            test_cases = ApiTestCase.query.filter(ApiTestCase.id.in_(case_ids)).all()
            for test_case in test_cases:
                case_param = []
                case_param.extend(VarRender.get_params_name(test_case.steps))
                case_param.extend(VarRender.get_params_name(test_case.expected))
                print("case_param", case_param)
                if "登录凭据" in case_param:
                    case_param.remove("登录凭据")
                # case_param 转 dict
                if len(case_param) > 0:
                    list_case_param.append({
                        "case_id": test_case.id,
                        "case_name": test_case.name,
                        # 字典推导式写法
                        "case_param": {key: "" for key in case_param}
                    })
        return respModel.ok_resp_simple_list(lst=list_case_param, msg="查询成功")
    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    """ 新增数据 """
    try:
        # 提交任务到线程池
        print(f"接收到数据:{request.json}")
        if not request.json.get("exec_param"):
            return respModel().error_resp(msg="用例参数不能为空")
        if not request.json.get("case_ids"):
            return respModel().error_resp(msg="用例ID不能为空")
        with app_server.app_context():
            request.json["id"] = None  # ID自增长
            request.json["exec_status"] = "初始化"
            request.json["exec_param"] = json.dumps(request.json["exec_param"], ensure_ascii=False)
            if request.json.get("created_at") is None:
                request.json["created_at"] = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
            data = module_model(**request.json)
            database.session.add(data)
            # 获取新增后的ID并返回
            database.session.flush()
            data_id = data.id
            database.session.commit()
        # 使用线程池运行异步函数
        executor.submit(asyncio.run, execute(data_id))
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(msg=f"添加失败:{e}")


from concurrent.futures import ThreadPoolExecutor

# 创建线程池，最多3个工作线程
executor = ThreadPoolExecutor(3)

async def execute(data_id):
    """执行测试任务"""
    with app_server.app_context():
        # 从数据库查询执行任务信息
        exec_task = module_model.query.filter_by(id=data_id).first()
        print("exec_task", exec_task.to_dict())
        # 从数据库查询项目信息
        project = Project.query.filter_by(id=exec_task.project_id).first()
        if exec_task:
            # 设置测试任务状态
            exec_task.exec_status = "执行中"
            # 更新执行任务的更新时间
            exec_task.updated_at = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
            # 提交数据库更新
            database.session.commit()
            # 解析用例ID字符串为列表
            case_ids = exec_task.case_ids.split(",")

            # 解析执行任务中的用例参数
            params = json.loads(exec_task.exec_param)
            print("params", params)
            # 提取 params 列表元素中的 case_id 作为key, 列表元素作为value 转成完整 dict对象
            case_params = {}
            for param in params:
                case_params[str(param["case_id"])] = param["case_param"]

            # 要执行的用例
            test_case = {}
            # 保存执行结果
            details = []
            # 执行成功的用例数
            success_count = 0
            # 执行失败的用例数
            failed_count = 0
            # 执行测试用例
            for case_id in case_ids:
                try:
                    print("执行用例ID:", case_id)
                    # 查询出需要执行的测试用例数据
                    test_case = ApiTestCase.query.filter_by(id=case_id).first()
                    # 如果不存在，直接返回错误
                    if not test_case:
                        return respModel.error_resp(msg=f"用例ID {case_id} 不存在")
                    # 获取当前用例的参数
                    case_param = case_params.get(case_id, {})
                    case_param.update(case_params.get('0', {}))  # 合并AI自动化系统配置参数
                    print("case_param", case_param)
                    # 渲染参数
                    steps = refresh(test_case.steps, case_param)
                    print("steps", steps)
                    expected = refresh(test_case.expected, case_param)
                    print("expected", expected)
                    request_info = json_utils.parse_json(steps)
                    print("request_info", request_info)
                    # 拼接URL
                    request_info['url'] = case_param.get("服务器地址", "") + request_info.get("path", "")
                    print(f'开始请求: {request_info}')
                    response_info = requests.request(
                        url=request_info['url'],
                        method=request_info.get("method", "GET"),
                        params=json_utils.parse_json(request_info.get("params")),
                        data=json_utils.parse_json(request_info.get("data", {})),
                        json={"password": "123456", "username": "18511114444"},
                        headers=json_utils.parse_json(request_info.get("headers", {})),
                        cookies=json_utils.parse_json(request_info.get("cookies", {}))
                    )
                    # 打印响应信息
                    print(f'请求结束: {response_info.status_code} {response_info.text}')
                    # 渲染提示词
                    ai_prompt = load_prompt("../prompts", "提示词-接口自动化测试断言.txt", {
                        "response_info": response_info,
                        "expected": expected,
                        "hint": ""
                    })
                    print("ai_prompt", ai_prompt)
                    # 创建OpenAI客户端
                    ai_client = OpenAI(api_key=project.llm_key,
                                       base_url=project.llm_url)

                    # 组装提示词
                    response = ai_client.chat.completions.create(
                        model=project.llm_model,
                        messages=[
                            {"role": "system", "content": "上下文"},
                            {"role": "user", "content": ai_prompt},
                        ],
                    )
                    # print("response", response)
                    content = response.choices[0].message.content
                    print("content", content)
                    # 提取生成的结果
                    generated_data = response.choices[0].message.content
                    # 提取```json 中的数据
                    str_result = re.search(r"```json(.*?)```", generated_data, re.DOTALL).group(1)
                    result = json.loads(str_result)
                    if result.get('success', False):
                        success_count += 1
                    else:
                        failed_count += 1

                    details.append({
                        "case_id": case_id,
                        "case_name": test_case.name,
                        "steps": request_info,
                        "expected": expected,
                        "ai_result": result,
                        "response_info": {
                            "status_code": response_info.status_code,
                            "headers": dict(response_info.headers),
                            "text": response_info.text,
                        },
                        "result": result.get('success', False),
                    })

                    # 更新执行任务状态并保存到数据库中
                    exec_task.exec_status = f"执行中..{success_count + failed_count}/{len(exec_task.case_ids)}"
                    exec_task.updated_at = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
                    database.session.commit()
                except Exception as e:
                    traceback.print_exc()
                    # 添加失败用例
                    failed_count += 1
                    details.append({
                        "case_id": case_id,
                        "case_name": test_case.name,
                        "steps": request_info,
                        "expected": expected,
                        "ai_result": {
                            "success": False,
                        }
                    })

            # 所有用例执行完成后，更新执行任务状态并保存到数据库中
            exec_task.exec_status = f"已结束"
            exec_task.details = json.dumps(details, ensure_ascii=False)
            exec_task.desc = f"成功{success_count}个用例，失败{failed_count}个用例"
            exec_task.updated_at = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
            database.session.commit()


        else:
            traceback.print_exc()