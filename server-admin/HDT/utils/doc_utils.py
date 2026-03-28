import re
import uuid


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
