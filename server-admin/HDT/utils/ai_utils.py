def load_prompt(temp_folder: str, name: str, context: dict):
    """
    加载ai的提示词模板并渲染
    :param temp_folder:
    :param name:
    :param context:
    :return:
    """
    from os import path
    # 可以渲染模板，将模板中的变量替换成实际值
    from jinja2 import Environment, FileSystemLoader
    # 当前文件目录
    folder = path.dirname(__file__)
    folder = path.join(folder, temp_folder)
    env = Environment(loader=FileSystemLoader(folder))
    template = env.get_template(name)
    # print("template", template)
    ai_prompt = template.render(context)
    # print("ai_prompt", ai_prompt)
    return ai_prompt

import os
from pathlib import Path
from openai import OpenAI

# 缓存文件路径
CACHE_DIR = os.path.join(Path.home(), ".ai_image_cache")
MAX_CACHE_SIZE = 500
def ai_image(image_id, image_base64, llm_key, base_url, llm_model, prompt, cache=True):
    """ 使用AI生成图片描述 """

    # 加一个缓存功能，把图片描述缓存到 /tmp 本地，下次请求的时候，如果图片描述已经缓存了，就不用再次请求了。最多缓存500张图片
    # 初始化缓存目录
    Path(CACHE_DIR).mkdir(exist_ok=True)

    # 缓存文件路径
    cache_file = os.path.join(CACHE_DIR, f"{image_id}.txt")

    # 检查缓存是否存在
    if os.path.exists(cache_file):
        print(f"使用缓存: {cache_file}")
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read()

    ai_client = OpenAI(api_key=llm_key, base_url=base_url)

    completion = ai_client.chat.completions.create(
        model= llm_model,
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
            {"type": "text", "text": prompt}
        ]}]
    )

    # 获取结果
    result = completion.choices[0].message.content

    # 保存到缓存文件（纯文本格式）
    try:
        if cache:
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(result)
    except:
        pass

    # 清理过期的缓存文件
    cleanup_cache()

    return result

def cleanup_cache():
    """清理超过最大缓存数量的旧文件"""
    if not os.path.exists(CACHE_DIR):
        return

    # 获取所有缓存文件并按修改时间排序（从旧到新）
    cache_files = sorted(
        Path(CACHE_DIR).glob("*.txt"),
        key=lambda f: f.stat().st_mtime
    )

    # 删除超过最大数量的旧文件
    while len(cache_files) > MAX_CACHE_SIZE:
        try:
            os.remove(cache_files.pop(0))  # 删除最旧的文件
        except:
            pass


def parse_markdown(markdown_text, llm_key, base_url, llm_model, prompt):
    """
    替换markdown中的图片为文字描述，并提取图片的alt文本
    """
    # 匹配Base64图片的正则表达式
    pattern = r'!\[(.*?)\]\(data:image/(?:png|jpeg|gif);base64,(.*?)\)'
    import re
    # 查找所有匹配的Base64图片
    matches = re.findall(pattern, markdown_text)

    # 如果没有找到图片，直接返回原文本和空列表
    if not matches:
        return markdown_text

    for i, (alt_text, image_data) in enumerate(matches, start=1):
        # 使用alt文本作为描述，如果没有则使用默认的"图片{i}"
        description = ai_image(alt_text.strip(), image_data, llm_key, base_url, llm_model, prompt)
        placeholder = f"> {description}"
        markdown_text = re.sub(
            r'!\[.*?\]\(data:image/(?:png|jpeg|gif);base64,' + re.escape(image_data) + r'\)',
            placeholder,
            markdown_text,
            count=1
        )
    return markdown_text


from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession
from mcp.client.sse import sse_client
async def mcp(ai_prompt: str, mcp_server: str, api_key, base_url, model):
    # 使用大模型连接mcp执行任务
    llm = ChatOpenAI(
        model=model,
        base_url=base_url,
        api_key=api_key
    )
    # 使用sse连接mcp服务器
    async with sse_client(mcp_server) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("✅ Connected to MCP Server")
            tools = await load_mcp_tools(session)
            agent = create_react_agent(llm, tools)
            agent_response = await agent.ainvoke(input={"messages": ai_prompt}, config={"recursion_limit": 99})

            print("✅ Agent Response:", agent_response['messages'][-1].content)
            return agent_response['messages'][-1].content
