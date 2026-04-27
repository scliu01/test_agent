import traceback
from datetime import datetime, timedelta

from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from HDT.utils.resp_model import respModel
from app import app_server, database
from HDT.models.projects import Project

# 路由名称
module_name = "project"
# 路由对象，在app.py中加载到flask对象中
module_route = Blueprint(f"route_{module_name}", __name__)
# 数据库模块名称
module_model = Project


# 查询所有数据
@module_route.route(f"/{module_name}/queryAll", methods=["GET"])
def queryAll():
    try:
        with app_server.app_context():
            # 获取查询所有数据的结果
            lst = module_model.query.all()
            # 对敏感字段进行脱敏处理
            masked_lst = []
            for item in lst:
                item_dict = item.to_dict()
                # 将敏感字段替换为 "******"
                if 'llm_key' in item_dict:
                    item_dict['llm_key'] = '******'
                if 'lvm_key' in item_dict:
                    item_dict['lvm_key'] = '******'
                masked_lst.append(item_dict)
            return respModel.ok_resp_list(lst=masked_lst, msg="查询成功")
    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/open", methods=["POST"])
def open_project():
    """ 打开项目 - 验证密码并返回访问令牌 """
    try:
        data = request.json
        if not data:
            return respModel.error_resp(msg="请提供JSON数据")

        project_id = data.get("project_id")
        password = data.get("password")

        if not project_id or not password:
            return respModel.error_resp(msg="项目ID或密码不能为空")

        with app_server.app_context():
            # 查询项目
            project = Project.query.filter_by(id=project_id).first()

            if not project:
                return respModel.error_resp(msg="项目不存在")

            # 验证密码
            if project.password != password:
                return respModel.error_resp(msg="密码错误")

            # 创建访问令牌，将项目ID放入token中
            additional_claims = {
                "project_id": project.id,
                "project_name": project.name
            }

            # 设置token过期时间（从配置中读取）
            expires_delta = timedelta(seconds=app_server.config.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))

            access_token = create_access_token(
                identity=str(project.id),
                additional_claims=additional_claims,
                expires_delta=expires_delta
            )

            # 返回token和项目信息（脱敏）
            project_info = project.to_dict()
            # 脱敏处理
            if 'llm_key' in project_info:
                project_info['llm_key'] = '******'
            if 'lvm_key' in project_info:
                project_info['lvm_key'] = '******'
            if 'password' in project_info:
                del project_info['password']  # 不返回密码

            return respModel.ok_resp(
                msg="密码正确",
                dic_t={
                    "access_token": access_token,
                    "token_type": "Bearer",
                    "expires_in": app_server.config.get("JWT_ACCESS_TOKEN_EXPIRES", 3600),
                    "project": project_info
                }
            )
    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(f"服务器错误，请联系管理员:{e}")


@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    """ 新增数据 """
    try:
        with app_server.app_context():
            # request.json获取POST请求的JSON数据
            print(f"接收到数据:{request.json}")
            request.json["id"] = None  # ID自增长
            # 如果已经没有created_at，就添加默认时间
            if request.json.get("created_at") is None:
                request.json["created_at"] = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
            data = module_model(**request.json)
            # 保存到数据库中
            database.session.add(data)
            # 获取新增后的ID并返回
            database.session.flush()
            data_id = data.id
            # 提交之后，数据才会真正保存到数据库中
            database.session.commit()
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.route(f"/{module_name}/queryById", methods=["GET"])
def queryById():
    """ 查询数据(单条记录) """
    try:
        data_id = int(request.args.get("id"))
        print(f"接收到数据:{data_id}")
        with app_server.app_context():
            # 数据库查询
            data = module_model.query.filter_by(id=data_id).first()
        if data:
            return respModel().ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    """ 修改数据 """
    try:
        with app_server.app_context():
            print(f"接收到数据:{request.json}")
            module_model.query.filter_by(id=request.json["id"]).update(request.json)
            database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")


@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
def delete():
    """ 删除数据 """
    try:
        data_id = int(request.args.get("id"))
        print(f"接收到数据:{data_id}")
        with app_server.app_context():
            project = module_model.query.filter_by(id=data_id).first()
            if project:
                database.session.delete(project)
                database.session.commit()
                return respModel.ok_resp(msg="删除成功")
            else:
                return respModel.error_resp(msg="项目不存在")
    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(f"服务器错误,删除失败：{e}")
