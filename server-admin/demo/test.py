dic = {'dictionary_id': '1', '服务器地址': 'https://maint_dev.jlksaas.net', '登录凭据': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxODA2MjQ2Mzk5NjcxNjY4NzM2IiwiZXhwIjoxNzc2NDIxNjQxfQ.fdbIt9DyCTAnYIyekiBJIkB2nzo49-CDPMDMgLHGMH8'}


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



case_param = convert_numeric_strings(dic)
print(case_param)