from HDT.utils.VarRender import refresh, fix_json_str
import json

def demo():
    # 原始数据
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
    # 直接转换会因为{{username}}导致报错，所以这里需要先处理这此数据
    # print("raw_json_str", raw_json_str)
    # json_data = json.loads(raw_json_str)
    # print("json_data", json_data)
    result = refresh(raw_json_str, {"username": "18511113333"})
    print("result", result)


# demo()


def demo02():
    # 原始数据
    raw_json_str = '返回状态码200，响应体中"code"为"200"，"msg"为"登录成功"，"data"中包含非空的"token"字段'
    result = refresh(raw_json_str, {"username": "18511113333"})
    print("result", result)

demo02()