import os
import re
import uuid


def demo():
    """
    需求规格说明书 - 示例.docx
    """
    # 文件路径
    temp_path = os.path.join(os.path.dirname(__file__), '需求规格说明书 - 示例.docx')
    # temp_path = os.path.join(os.path.dirname(__file__), '学生端登录接口文档0901002.md')
    print("temp_path", temp_path)
    # 获取文件类型后缀
    file_extension = os.path.splitext(temp_path)[1]
    print("file_extension", file_extension)
    # 限制最大标题层级
    max_level = 2
    if file_extension == '.docx':
        from markitdown import MarkItDown

        md = MarkItDown(enable_plugins=True)
        full_markdown_text = md.convert(temp_path, keep_data_uris=True).text_content
    else:
        with open(temp_path, 'r', encoding='utf-8') as f:
            full_markdown_text = f.read()

    print("full_markdown_text", full_markdown_text)

    # 使用 langchain_text_splitters 拆分Markdown
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

    for i, md_split in enumerate(md_splits):
        metadata = md_split.metadata
        print("metadata", metadata)
        markdown_text = md_split.page_content
        print("markdown_text", markdown_text)
        text_content = generate_image_uuid(markdown_text)
        print("text_content", text_content)


def generate_image_uuid(markdown_text):
    """
    为Markdown中的所有图片生成新的UUID替代文本
    无论原图是否有替代文本，都替换为新的UUID
    """
    pattern = r'!\[(.*?)\]\((data:image/(?:png|jpeg|gif);base64,.*?)\)'

    # 替换函数 - 总是生成新的UUID
    def replace_match(match):
        image_data = match.group(2)
        return f"![{str(uuid.uuid4()).replace('-', '')}]({image_data})"

    # 使用sub进行全部替换
    return re.sub(pattern, replace_match, markdown_text)


demo()

def save_doc():
    """
        需求规格说明书 - 示例.docx
        """
    # 文件路径
    temp_path = os.path.join(os.path.dirname(__file__), '需求规格说明书 - 示例.docx')
    # temp_path = os.path.join(os.path.dirname(__file__), '学生端登录接口文档0901002.md')
    print("temp_path", temp_path)
    # 获取文件类型后缀
    file_extension = os.path.splitext(temp_path)[1]
    print("file_extension", file_extension)
    # 限制最大标题层级
    max_level = 2
    if file_extension == '.docx':
        from markitdown import MarkItDown

        md = MarkItDown(enable_plugins=True)
        full_markdown_text = md.convert(temp_path, keep_data_uris=True).text_content
    else:
        with open(temp_path, 'r', encoding='utf-8') as f:
            full_markdown_text = f.read()

    print("full_markdown_text", full_markdown_text)

    # 使用 langchain_text_splitters 拆分Markdown
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



    for i, md_split in enumerate(md_splits):
        metadata = md_split.metadata
        print("metadata", metadata)
        markdown_text = md_split.page_content
        print("markdown_text", markdown_text)
        text_content = generate_image_uuid(markdown_text)
        print("text_content", text_content)
