import ast
import json
from concurrent.futures.thread import ThreadPoolExecutor

import requests
from openai import OpenAI

from HDT.utils.VarRender import get_params_name, refresh, fix_json_str
from HDT.utils.ai_utils import load_prompt


def demo_login():
    # 请求的相关信息
    request_info = {
        "url": "http://novel.hctestedu.com/user/login",
        "method": "POST",
        "params": {
            "application": "app",
            "application_client_type": "weixin"
        },
        "data": {
            "username": 18511114444,
            "password": 1234561
        },
    }
    # 发起请求
    res = requests.request(**request_info)
    print("响应结果内容", res.text)
    print("响应状态码", res.status_code)
    print("响应结果内容的json", res.json())
    # 取出 msg
    msg = res.json()["msg"]
    assert msg == "SUCCESS"


# demo_login()


def 单个接口断言():
    request_info = {
        "url": "http://novel.hctestedu.com/user/login",
        "method": "POST",
        "params": {
            "application": "app",
            "application_client_type": "weixin"
        },
        "data": {
            "username": 18511114444,
            "password": 123456
        },
    }
    response_info = requests.request(**request_info)
    # print("响应结果", response_info)
    # print("响应状态码", response_info.status_code)
    # print("响应结果", response_info.text)

    ai_prompt = load_prompt("../prompts", "提示词-接口自动化测试断言.txt", {
        "response_info": response_info,
        "expected": '返回状态码200，响应体中code为"200"，msg为"success"，data中包含有效token',
        "hint": "将token保存到返回结果中"
    })
    # print("ai_prompt", ai_prompt)
    # 创建OpenAI客户端
    ai_client = OpenAI(api_key="sk-1a1085539a654a3eaf15ec230b086136",
                       base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
    # 组装提示词
    response = ai_client.chat.completions.create(
        model="qwen3-max",
        messages=[
            {"role": "system", "content": "上下文"},
            {"role": "user", "content": ai_prompt},
        ],
    )
    # print("response", response)
    content = response.choices[0].message.content
    print("content", content)

executor = ThreadPoolExecutor(max_workers=3)
# 单个接口断言()
for i in range(1, 10):
    print(f"任务第{i}开始执行")
    # 单个接口断言()
    executor.submit(单个接口断言)
    print(f"任务第{i}结束执行")


def get_params():
    test_case = {
        "steps": "发起POST请求到{{ server_url }}/user/login，请求体为{{ steps.data }}",
        "expected": "返回状态码200，响应体中code为\"200\"，msg为\"success\"，data中包含有效token，token值为{{ token }}",
    }
    # 保存所有提取出来的参数名称
    case_param = []
    # jinja2 提取文本中需要的变量
    # from jinja2 import Environment, meta
    # env = Environment()
    # parsed_content = env.parse(test_case["steps"])
    # print("parsed_content", parsed_content)
    # case_param.extend(list(meta.find_undeclared_variables(parsed_content)))
    # print("case_param1", case_param)
    # parsed_content = env.parse(test_case["expected"])
    # case_param.extend(list(meta.find_undeclared_variables(parsed_content)))
    # print("case_param2", case_param)
    case_param.extend(get_params_name(test_case["steps"]))
    case_param.extend(get_params_name(test_case["expected"]))
    print("case_param1", case_param)


# get_params()


def 复杂json格式处理():
    raw_json_str = '''
        {
            "data": "{}",
            "json": "{\"password\":\"123456\",\"username\":\"{{username}}\"}",
            "path": "/user/login",
            "params": "{}",
            "cookies": "{}",
            "headers": "{\"Content-Type\":\"application/json\"}",
            "method": "POST"
        }
    '''
    # json_str = json.loads(raw_json_str)
    # print("json_str", json_str)
    json_str = fix_json_str(raw_json_str)
    print("json_str", json_str)
    # json.loads无法处理带有单引号的json字符串
    # json_data = json.loads(json_str)
    # 处理字面量数据，"",10
    # json_data = ast.literal_eval(json_str)
    # print("json_data", type(json_data), json_data)
    json_data = refresh(json_str, {})
    print("json_data", type(json_data), json_data)



# 复杂json格式处理()

