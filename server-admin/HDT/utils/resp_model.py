# 模板代码
""""
返回值模板
"""
import  json
class respModel():

    @staticmethod
    def ok_resp(obj=None,msg=None,dic_t=None):
        rsp={}
        rsp["code"] = 200
        rsp["msg"] = msg
        data={}
        if obj:
            attr_data = respModel.get_custom_attributes(obj)
            if isinstance(attr_data, dict):
                data.update(attr_data)
        if dic_t and isinstance(dic_t, dict):
            data.update(dic_t)
        rsp["data"] = data
        return rsp

    @staticmethod
    def ok_resp_list(obj=None,msg=None,lst=None,total=0,page=1,pageSize=10):
        rsp = {}
        rsp["code"] = 200
        rsp["msg"] = msg
        rsp["total"] = total
        rsp["page"] = page
        rsp["pageSize"] = pageSize
        lst1 =[]
        if lst:
            for obj in lst:
                dic = respModel.get_custom_attributes(obj)
                lst1.append(dic)
        rsp["data"] = lst1
        return rsp

    @staticmethod
    def ok_resp_listdata(obj=None,msg=None,lst=None,total=0,page=1,pageSize=10):
        # 自己拼的数据，不需要获取对应的属性
        rsp = {}
        rsp["code"] = 200
        rsp["msg"] = msg
        rsp["total"] = total
        rsp["page"] = page
        rsp["pageSize"] = pageSize
        rsp["data"] = lst
        return rsp

    @staticmethod
    def ok_resp_simple(lst=None,msg=None):
        rsp = {}
        rsp["code"] = 200
        rsp["msg"] = msg
        rsp["data"] = lst
        return rsp

    @staticmethod
    def ok_resp_simple_list(lst=None, msg=None,total=0):
        rsp = {}
        rsp["code"] = 200
        rsp["msg"] = msg
        rsp["data"] = lst
        rsp["total"] = total
        return rsp

    @staticmethod
    def ok_resp_text(msg=None,data=None):
        rsp = {}
        rsp["code"] = 200
        rsp["msg"] = msg
        rsp["data"] = data
        return rsp

    # 新定义一个response模块，处理树形数据返回的。。。
    @staticmethod
    def ok_resp_tree(treeData,msg):
        rsp = {}
        rsp["code"] = 200
        rsp["msg"] = msg
        rsp["data"] = treeData
        return rsp


    @staticmethod
    def error_resp(msg):
        rsp = {}
        rsp["code"] = -1
        rsp["msg"] = msg
        return rsp

    @staticmethod
    def get_custom_attributes(obj):
        custom_attributes = {}
        # 优先使用模型自定义的to_dict方法（如果存在）
        if hasattr(obj, 'to_dict') and callable(obj.to_dict):
            return obj.to_dict()
        # 检查是否为SQLAlchemy模型实例
        elif hasattr(obj, '__table__'):
            # 处理SQLAlchemy模型
            attributes = {column.name: getattr(obj, column.name) for column in obj.__table__.columns}
        elif isinstance(obj, dict):
            # 处理字典对象
            attributes = obj
        else:
            # 获取普通对象的属性
            attributes = vars(obj)
        # 过滤掉内置属性和方法
        for attribute, value in attributes.items():
            if not attribute.startswith('__') and not callable(value) and not attribute.startswith('_'):
                # 时间格式转换, 如果是 datetime
                from datetime import datetime
                if isinstance(value, datetime):
                    value = datetime.strftime(value, '%Y-%m-%d %H:%M:%S')

                custom_attributes[attribute] = value
        return custom_attributes