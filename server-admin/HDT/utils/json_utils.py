import re
import json
import ast


def parse_json(target: str):
    """
    转换成json
    :param target:
    :return:
    """
    try:
        # 如果不是字符串，则直接返回
        if not isinstance(target, str):
            return target
        return json.loads(target)
    except Exception as e:
        print("json.loads error:", e)
        return ast.literal_eval(target)


def fix_unquoted_templates(text):
    """
    修复AI异常json数据
    # 匹配 : 后面的 {{ ... }} 或 [ 后面的 {{ ... }}
    # 模式1: ": {{ ... }}" -> 已经是字符串，不需要处理
    # 模式2: : {{ ... }} (没有引号) -> 需要添加引号

    # 处理 ": {{ ... }}" 这种情况，保持原样
    # 处理 : {{ ... }} 或 [ {{ ... }} 这种情况，添加引号
    :param text:
    :return:
    """
    # 匹配冒号后面跟着空格和{{的情况（不在引号内）
    pattern1 = r'(:\s*)\{\{([^}]+)\}\}'
    text = re.sub(pattern1, lambda m: f'{m.group(1)}"{{{{{m.group(2)}}}}}"', text)

    # 匹配左方括号后面跟着空格和{{的情况（不在引号内）
    pattern2 = r'(\[\s*)\{\{([^}]+)\}\}'
    text = re.sub(pattern2, lambda m: f'{m.group(1)}"{{{{{m.group(2)}}}}}"', text)

    return text

def convert_numeric_strings(obj):
    """
    递归地将字典或列表中字符串形式的数值转换为整数或浮点数

    Args:
        obj: 可以是字典、列表或其他类型

    Returns:
        转换后的对象
    """
    if isinstance(obj, dict):
        return {key: convert_numeric_strings(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numeric_strings(item) for item in obj]
    elif isinstance(obj, str):
        # 尝试转换为整数
        try:
            int_value = int(obj)
            # 检查是否真的是整数（排除像"001"这样的情况）
            if str(int_value) == obj or (obj.startswith('-') and str(int_value) == obj):
                return int_value
        except (ValueError, OverflowError):
            pass

        # 尝试转换为浮点数
        try:
            float_value = float(obj)
            # 确保是有效的浮点数格式（包含小数点或科学计数法）
            if '.' in obj or 'e' in obj.lower():
                return float_value
        except (ValueError, OverflowError):
            pass

        # 保持原样
        return obj
    else:
        return obj
