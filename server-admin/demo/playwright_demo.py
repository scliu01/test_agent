import asyncio

from playwright.sync_api import sync_playwright

from HDT.utils import ai_utils
from HDT.utils.ai_utils import load_prompt


def demo():
    with sync_playwright() as p:
        # 启动 Chrome 浏览器
        browser = p.chromium.launch(headless=False)  # headless=False 显示浏览器界面，True 为无头模式（后台运行）
        page = browser.new_page()
        # 访问百度
        page.goto("https://www.baidu.com")
        # 打印页面标题
        print("页面标题：", page.title())
        # 关闭浏览器
        browser.close()


# demo()

async def mcp_demo():
    context = {
        "steps": [
            {"action": "打开百度", "url": "http://www.baidu.com"},
            {"action": "输入搜索关键词", "keyword": "Playwright"},
            {"action": "点击搜索按钮"},
        ],
        "expected": "搜索结果中包含关键词 Playwright",
        "device_type": "android",
        "mcp_file_path": r"http://8.162.0.206:5001/tmp/mobile_mcp",
    }
    # ai_prompt = load_prompt("../prompts", "提示词-WEB自动化测试执行.txt", context)
    ai_prompt = load_prompt("../prompts", "提示词-APP自动化测试执行.txt", context)
    print("ai_prompt", ai_prompt)
    # 使用大模型连接mcp执行任务
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(
        model="qwen3-max-preview",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key="sk-1a1085539a654a3eaf15ec230b086136"
    )
    # PLAYWRIGHT_MCP_SERVER = "http://localhost:8931/sse"
    MOBILE_MCP_SERVER = "http://localhost:8932/mcp"
    from langgraph.prebuilt import create_react_agent
    from langchain_mcp_adapters.tools import load_mcp_tools
    from mcp import ClientSession
    from mcp.client.sse import sse_client
    # 使用sse连接mcp服务器
    async with sse_client(MOBILE_MCP_SERVER) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("✅ Connected to MCP Server")
            tools = await load_mcp_tools(session)
            agent = create_react_agent(llm, tools)
            agent_response = await agent.ainvoke(input={"messages": ai_prompt}, config={"recursion_limit": 99})

            print("✅ Agent Response:", agent_response['messages'][-1].content)
            return agent_response['messages'][-1].content


# asyncio.run(mcp_demo())

from HDT.config.dev_settings import PLAYWRIGHT_MCP_SERVER, MOBILE_MCP_SERVER, PLAYWRIGHT_MCP_FILE_PATH, \
    MOBILE_MCP_FILE_PATH
from HDT.utils.ai_utils import mcp


async def mcp_demo2():
    context = {
        "steps": [
            {"action": "打开百度", "url": "https://www.baidu.com"},
            {"action": "输入搜索关键词", "keyword": "Playwright"},
            {"action": "点击搜索按钮"},
        ],
        "expected": "搜索结果中包含关键词 Playwright",
        "mcp_file_path": PLAYWRIGHT_MCP_FILE_PATH,
        "device_type": "android",
        # "mcp_file_path": r"http://8.162.0.206:5001/tmp/mobile_mcp",
        # "device_type": "ios"
    }
    task_type = "mobile"  # mobile, web
    ai_prompt = load_prompt("../prompts", "提示词-WEB自动化测试执行.txt", context)
    if task_type == "mobile":
        context["mcp_file_path"] = MOBILE_MCP_FILE_PATH
        ai_prompt = load_prompt("../prompts", "提示词-APP自动化测试执行.txt", context)
    print("ai_prompt", ai_prompt)
    mcp_server = PLAYWRIGHT_MCP_SERVER
    if task_type == "mobile":
        mcp_server = MOBILE_MCP_SERVER
    ai_result = await mcp(ai_prompt, mcp_server, api_key="sk-1a1085539a654a3eaf15ec230b086136",
                          base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", model="qwen3-max-preview")
    print("ai_result", ai_result)


asyncio.run(mcp_demo2())


from playwright.sync_api import sync_playwright
import cv2
import numpy as np
import base64
import uuid


def webpage_as_image(url, color_threshold=10, sample_height=10):
    with sync_playwright() as p:
        # 启动浏览器（这里使用Chromium，也可以选择firefox或webkit）
        browser = p.chromium.launch(headless=True)  # headless=True 表示无头模式
        page = browser.new_page()  # 创建新页面
        page.set_viewport_size({"width": 1920, "height": 5000})  # 设置大视口
        page.goto(url, timeout=60000)  # 访问指定网址
        page.wait_for_load_state("networkidle")  # 最终等待确保所有资源加载
        page.wait_for_timeout(2000)
        screenshot_bytes = page.screenshot(full_page=True, type="jpeg")
        browser.close()  # 关闭浏览器
    # original_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')  # 转换为 Base64 字符串（如果后续需要字符串形式）
    # # 保存为文件
    # filename = f"调试.jpg"
    # with open(filename, "wb") as f:
    #     f.write(base64.b64decode(screenshot_base64_str))
    # 原始Base64转换（备用）
    original_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')

    # 裁剪顶部+底部纯色区域
    try:
        # 解码为OpenCV图像
        img_array = np.frombuffer(screenshot_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            print("无法解码截图")
            return original_base64

        height, width = img.shape[:2]
        top_y = 0  # 顶部有效区域起始行
        bottom_y = height - 1  # 底部有效区域结束行

        # ========== 第一步：检测并裁剪顶部纯色区域 ==========
        # 采样顶部sample_height行的平均颜色
        top_sample = img[:sample_height, :]
        top_avg_color = np.mean(top_sample, axis=(0, 1))
        # 从上往下找第一个颜色差异超过阈值的行
        for y in range(0, height):
            row = img[y, :]
            diff = np.mean(np.abs(row - top_avg_color))
            if diff > color_threshold:
                top_y = y  # 确定顶部有效区域起始位置
                break

        # ========== 第二步：检测并裁剪底部纯色区域 ==========
        # 采样底部sample_height行的平均颜色
        bottom_sample = img[-sample_height:, :]
        bottom_avg_color = np.mean(bottom_sample, axis=(0, 1))
        # 从下往上找第一个颜色差异超过阈值的行
        for y in range(height - 1, -1, -1):
            row = img[y, :]
            diff = np.mean(np.abs(row - bottom_avg_color))
            if diff > color_threshold:
                bottom_y = y  # 确定底部有效区域结束位置
                break

        # ========== 第三步：裁剪有效区域（顶部→底部） ==========
        cropped_img = img[top_y:bottom_y + 1, :]

        # 编码为Base64返回
        _, buffer = cv2.imencode('.jpg', cropped_img)
        cropped_base64 = base64.b64encode(buffer).decode('utf-8')

        print(f"裁剪完成：原始尺寸{height}x{width} → 裁剪后{cropped_img.shape[0]}x{cropped_img.shape[1]}")
        return cropped_base64

    except Exception as e:
        print(f"裁剪过程中出错: {str(e)}")
        return original_base64  # 出错时返回原始Base64


def 监控数据提取():
    url = "https://img2018.cnblogs.com/blog/874963/201908/874963-20190802143825975-2053857734.png"
    image_base64 = webpage_as_image(url)
    print("image_base64", image_base64)
    # 保存为文件
    filename = f"调试1.jpg"
    with open(filename, "wb") as f:
        f.write(base64.b64decode(image_base64))
    image_parse_prompt = load_prompt("../prompts", "提示词-性能压测-监控数据提取.txt", {})
    result = ai_utils.ai_image(str(uuid.uuid4()), image_base64, "sk-1a1085539a654a3eaf15ec230b086136",
                               "https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen3-vl-plus", image_parse_prompt)
    print("result", result)


# 监控数据提取()


def 性能分析():
    data = {
        "id": 15,
        "configs": [{"id": 1755508452720, "name": "CPU",
                     "source_url": "http://192.168.1.128:3000/d/9CWBzd1f0bik001/linuxzhu-ji-xing-neng-jian-kong?from={{start_time}}&to={{end_time}}&var-project=&var-job=nodes&var-node=192.168.1.128:9100&var-hostname=localhost.localdomain&var-device=enp0s3&var-maxmount=%2F&var-show_hostname=localhost.localdomain&kiosk&viewPanel=7"},
                    {"id": 1755516825082, "name": "Linux服务器",
                     "source_url": "http://192.168.1.128:3000/d/9CWBzd1f0bik001/linuxzhu-ji-xing-neng-jian-kong?orgId=1&var-project=All&var-job=nodes&var-node=192.168.1.172:9100&var-hostname=localhost.localdomain&var-device=enp0s3&var-maxmount=%2F&var-show_hostname=localhost.localdomain&from=1755516600000&to=1755516720000&kiosk"},
                    {"id": 1755516831612, "name": "jmeter",
                     "source_url": "http://192.168.1.128:3000/d/W-LRIAYVk/jmeterxing-neng-ce-shi-shi-shi-jian-kong?orgId=1&var-data_source=InfluxDB&var-application=step%E6%B5%8B%E8%AF%95&var-transaction=&var-measurement_name=jmeter&var-send_interval=5&from=1755516600000&to=1755516720000"},
                    {"id": 1755516839273, "name": "JVM",
                     "source_url": "http://192.168.1.128:3000/d/jvm-dashboard/jvm-xu-ni-ji-xing-neng-jian-kong?from=1755516600000&to=1755516720000"}
                    ]
    }
    # 图片说明信息
    source_items = []
    configs = data["configs"]
    for config in configs:
        print("config", config)
        url = config["source_url"]
        image_base64 = webpage_as_image(url)
        print("image_base64", image_base64)
        image_parse_prompt = load_prompt("../prompts", "提示词-性能压测-监控数据提取.txt", {})
        result = ai_utils.ai_image(str(uuid.uuid4()), image_base64, "sk-1a1085539a654a3eaf15ec230b086136",
                                   "https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen3-vl-plus",
                                   image_parse_prompt)
        source_items.append({
            "title": config["name"],
            "content": result
        })
    ai_prompt = load_prompt("../prompts", "提示词-性能分析.txt", {
        "source_items": source_items,
    })
    print(f"生成的提示词 ai_prompt: {ai_prompt}")
