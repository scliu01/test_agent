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
