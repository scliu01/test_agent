import asyncio
import json
import re
import time

import requests
from openai import OpenAI, AsyncOpenAI

from HDT.utils.ai_utils import load_prompt


# 定义一个耗时的异步任务（模拟接口调用/数据库查询）
async def async_task(task_name, delay):
    print(f"任务 {task_name} 开始执行，预计耗时 {delay} 秒")
    # await只能写在async函数中
    await asyncio.sleep(delay)
    print(f"任务 {task_name} 执行完成")
    return f"任务 {task_name} 结果"


# 依次执行多个任务，如何实现并发执行
# asyncio.run(async_task("A", 2))
# asyncio.run(async_task("B", 1))


# 同步执行对比（用于凸显asyncio的优势）
def sync_tasks():
    print("=== 同步执行 ===")
    start_time = time.time()
    # 同步执行，依次等待每个任务完成
    time.sleep(2)  # 模拟任务1
    time.sleep(3)  # 模拟任务2
    time.sleep(1)  # 模拟任务3
    end_time = time.time()
    print(f"同步执行总耗时：{end_time - start_time:.2f} 秒")


# sync_tasks()

# 泡面，烧水5分钟，拆包装要1分钟，泡面3分钟，一共要9分钟
# 如何优化？先烧水，再拆包装，等水烧好了再泡面，一共要8分钟

# 异步并发执行
async def async_tasks():
    start_time = time.time()
    # 方式1：用asyncio.gather()批量执行协程，等待所有协程完成并收集结果
    result = await asyncio.gather(
        async_task("A", 2),
        async_task("B", 3),
        async_task("C", 1)
    )
    end_time = time.time()
    print(f"异步并发执行总耗时：{end_time - start_time:.2f} 秒")
    # 打印所有任务结果
    print("所有任务结果：", result)


# asyncio.run(async_tasks())


async def async_ai_task_demo():
    # 取出一条数据库中的数据
    case_list = [{
        "created_at": "2026-01-17T19:53:15",
        "expected": "返回状态码200，响应体中code为\"200\"，msg为\"success\"，data中包含有效token，token值为{{ token }}",
        "id": 580,
        "module_id": 1271,
        "name": "使用正确的手机号和密码登录成功",
        "precondition": "用户已使用手机号完成注册，且账号处于正常状态",
        "priority": "1",
        "project_id": 1,
        "steps": {
            "path": "/user/login",
            "method": "POST",
            "params": {},
            "json": {},
            "data": {
                "username": "18511114444",
                "password": "123456"
            },
            "headers": {},
            "cookies": {}
        },
        "updated_at": "2026-01-17T11:59:39",
        "hint": "提取响应内容中的token并显示在最终返回的结果中"
    }, {
        "created_at": "2026-01-17T21:55:28",
        "expected": "返回状态码200，响应体中code为成功标识（如\"200\"或\"0\"），data包含pageNum=\"1\"、pageSize=\"10\"、total大于等于1，list数组中包含至少一个书籍对象，每个对象包含bookId、bookName、lastIndexName等字段",
        "id": 590,
        "module_id": 1278,
        "name": "正常分页查询我的书架数据",
        "precondition": "用户已登录，并且在“我的书架”中存在至少一条书籍记录",
        "priority": "1",
        "project_id": 1,
        "steps": {
            "path": "/user/listBookShelfByPage",
            "method": "GET",
            "params": {
                "curr": "1",
                "limit": "10"
            },
            "headers": {
                "Authorization": "{{ token }}"
            }
        },
        "updated_at": "2026-01-17T13:55:29",
        "hint": ""
    }]
    server_url = "http://novel.hctestedu.com"
    # 创建OpenAI客户端
    ai_client = AsyncOpenAI(api_key="sk-1a1085539a654a3eaf15ec230b086136",
                            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
    tasks = []
    for obj in case_list:
        tasks.append(async_ai_task(obj, server_url, ai_client))
    await asyncio.gather(*tasks)


async def async_ai_task(obj, server_url, ai_client):
    print("任务开始")
    # obj = Template(str(obj)).render(context)
    # print("obj", type(obj), obj)
    # 替换单引号为双引号（需要更精确的处理）
    # 使用 ast.literal_eval 安全地解析 Python 字面量
    # obj = ast.literal_eval(obj)
    # 取出参数发起请求
    response_info = requests.request(**{
        "url": server_url + obj.get('steps', {}).get('path', ''),
        "method": obj.get('steps', {}).get('method', ''),
        "params": obj.get('steps', {}).get('params', {}),
        "data": obj.get('steps', {}).get('data', {}),
        "json": obj.get('steps', {}).get('json', {}),
        "headers": obj.get('steps', {}).get('headers', {}),
        "cookies": obj.get('steps', {}).get('cookies', {}),
    })
    # print("响应结果", response_info.text)

    ai_prompt = load_prompt("../prompts", "提示词-接口自动化测试断言.txt", {
        "response_info": response_info,
        "expected": obj.get('expected', ''),
        "hint": obj.get('hint', '')
    })
    # print("ai_prompt", ai_prompt)
    # 组装提示词
    response = await ai_client.chat.completions.create(
        model="qwen3-max",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": ai_prompt},
        ],
    )
    print("response", response)
    content = response.choices[0].message.content
    print("content", content)
    json_data = re.search(r"```json(.*?)```", content, re.DOTALL)
    if json_data:
        json_content = json_data.group(1)
        parsed_data = json.loads(json_content)
        print("parsed_data", parsed_data)


if __name__ == "__main__":
    # 先执行同步任务
    # print("=== 同步执行 ===")
    # sync_tasks()

    # async_task("A", 2)
    # for i in range(1, 10):
    #     print(f"任务第{i}开始执行")
    #     asyncio.run(async_task(f"A{i}", 2))
    #     print(f"任务第{i}结束执行")
    # asyncio.run(async_task("A", 2))
    # # 再执行异步任务
    # print("\n=== 异步并发执行 ===")
    # asyncio.run(async_tasks())
    asyncio.run(async_ai_task_demo())
