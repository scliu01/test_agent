# -*- coding: utf-8 -*-
# 字符串模板进行参数渲染
# 使用 jinjia2 模板引擎 (类似 flask的模板)
# https://docs.jinkan.org/docs/jinja2/templates.html
from jinja2 import Template, Environment, meta
import ast
# 标准化Unicode字符（全角转半角）
import unicodedata

def refresh(target, context):
    target_str = str(target)
    try:
        if target is None: return None
        # 去除全角输入的内容
        normalized_text = unicodedata.normalize('NFKC', target_str)
        fix_result = fix_json_str(normalized_text)
        print("fix_result", fix_result)
        # 必须是以{或者[开头的字符串，才需要使用ast.literal_eval处理
        if fix_result.startswith('{') or fix_result.startswith('['):
            target_str = ast.literal_eval(fix_result)
        return Template(str(target_str)).render(context)
    except Exception as e:
        print("refresh error", e)
        return Template(target_str).render(context)


def fix_json_str(json_str: str):
    """
    修复 JSON 字符串中的引号问题，例如下面的数据
    "{\"password\":\"123456\",\"username\":\"{{username}}\"}",
    如果直接使用refresh会出现"{"password":"123456","username":"18511113333"}",这种不符合语法的错误
    """
    json_str = json_str.replace('"{', '\'{')
    json_str = json_str.replace('}"', '}\'')
    json_str = json_str.replace('"[', '\'[')
    json_str = json_str.replace(']"', ']\'')
    json_str = json_str.replace('\'{{', '"{{')
    json_str = json_str.replace('}}\'', '}}"')
    # 去掉换行符
    json_str = json_str.replace('\n', '')
    # 去掉空格
    json_str = json_str.replace(' ', '')

    return json_str


def get_params_name(target):
    """
        使用 jinja2 提取文本中需要的变量
    :param target:
    :return:
    """
    env = Environment()
    parsed_content = env.parse(str(target))
    return list(meta.find_undeclared_variables(parsed_content))


def test_refresh():
    # 单元测试用例 - 检查refresh是否有效
    target = "hello {{name}}, {{niasd}}"
    context = {"name": "张三"}
    result = refresh(target, context)
