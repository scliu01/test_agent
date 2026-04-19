# -*- coding: utf-8 -*-
# 字符串模板进行参数渲染
# 使用 jinjia2 模板引擎 (类似 flask的模板)
# https://docs.jinkan.org/docs/jinja2/templates.html
from jinja2 import Template, Environment, meta
import ast
# 标准化Unicode字符（全角转半角）
import unicodedata

def refresh(target, context):
    # target_str = str(target)
    # try:
    #     if target is None: return None
    #     # 去除全角输入的内容
    #     normalized_text = unicodedata.normalize('NFKC', target_str)
    #     fix_result = fix_json_str(normalized_text)
    #     print("fix_result", fix_result)
    #     # 必须是以{或者[开头的字符串，才需要使用ast.literal_eval处理
    #     if fix_result.startswith('{') or fix_result.startswith('['):
    #         target_str = ast.literal_eval(fix_result)
    #
    #     return Template(target_str).render(context)
    # except Exception as e:
    #     print("refresh error", e)
    #     return Template(target_str).render(context)
    target_str = str(target)
    # print("target_str", target_str)
    # print("context", context)
    try:
        if target is None: return None
        normalized_text = unicodedata.normalize('NFKC', target_str)  # 去除全角输入的内容
        fix_result = fix_json_str(normalized_text)
        # print("fix_result", fix_result)
        # 必须是以{或者[开头的字符串，才需要使用ast.literal_eval处理
        if fix_result.startswith('{') or fix_result.startswith('['):
            try:
                evaluated = ast.literal_eval(fix_result)  # 尝试使用ast.literal_eval进行评估
                # 如果评估结果是dict或list，需要转回JSON字符串才能进行模板渲染
                if isinstance(evaluated, (dict, list)):
                    import json
                    target_str = json.dumps(evaluated, ensure_ascii=False)  # 转回JSON字符串
                else:
                    target_str = str(evaluated)  # 否则直接返回字符串
            except (ValueError, SyntaxError):
                # 如果literal_eval失败，使用原始字符串
                target_str = fix_result
        else:
            target_str = fix_result
        # print("target_str2:", target_str)
        return Template(target_str).render(context)
    except Exception as e:
        print("refresh error", e)
        return Template(str(target)).render(context)


def get_params_name(target):
    """
        使用 jinja2 提取文本中需要的变量
    :param target:
    :return:
    """
    env = Environment()
    parsed_content = env.parse(str(target))
    return list(meta.find_undeclared_variables(parsed_content))


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





if __name__ == '__main__':
    dic = """"{"path":"/api/dictionaries/{{ dictionary_id }}/data","method":"POST","json":{"dictionary_id":"{{ dictionary_id }}","data_name":"A","data_key":-1,"sort_value":0,"is_enable":2,"remark":"非常长的备注信息非常长的备注信息非常长的备注信息非常长的备注信息非常长的备注信息非常长的备注信息"}}
    """
    target = "hello {{name}}, {{niasd}}"
    context = {'dictionary_id': 1, '服务器地址': 'https://maint_dev.jlksaas.net', '登录凭据': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxODA2MjQ2Mzk5NjcxNjY4NzM2IiwiZXhwIjoxNzc2NDI4NDY0fQ.QGZbSGaVSfhT2WoRYewI1SolrfMSs1ioKKIjlGUJVAw'}
    result = refresh(dic, context)
    print(result, type(result))
