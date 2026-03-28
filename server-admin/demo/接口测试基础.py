import requests


def demo_get():
    params = {"project_id": "1", "module_id": "789"}
    # 最简单的GET请求，通过params指定get请求参数
    response = requests.get("http://localhost:5001/api_test_case/queryAll", params=params)
    print(f"响应结果: {response}")
    # 处理JSON响应
    result = response.json()
    print(f"result: {result}")


def demo_json():
    data = {
        "page": 1,
        "pageSize": 5,
        "project_id": "1",
        "module_id": 789
    }
    # 通过json指定post请求的json参数
    response = requests.post("http://localhost:5001/api_test_case/queryByPage", json=data)
    result = response.json()
    print(f"result: {result}")


def demo_post():
    # 发送 POST 请求，访问登录接口
    # 准备登录数据
    data = {
        "username": "18511113333",
        "password": "a123456"
    }
    # 发送请求，通过data参数指定post请求的表单参数
    response = requests.post('http://novel.hctestedu.com/user/login', data=data)
    print("发送 POST 请求", response)
    # Response类型提供了json()方法，返回json格式的响应结果
    res_json = response.json()  # 响应数据
    print("响应结果", res_json)

    # 获取token，在下一个接口要使用，这个写法要结合实际的响应结果来写
    token = res_json['data']['token']
    print("token", token)

    # 访问我的书架接口，因为我的书架接口需要登录，所以需要带token
    # 将token按接口要求添加到headers中
    headers = {
        "Cookie": f"Authorization={token}"
    }
    # 通过headers参数指定请求头参数
    response = requests.get(
        f'http://novel.hctestedu.com/user/listBookShelfByPage?curr=1&limit=10',
        headers=headers)
    print("我的书架", response.json())


if __name__ == '__main__':
    # demo_get()
    demo_post()
