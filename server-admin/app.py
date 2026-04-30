import os
import urllib

from flask import Flask, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from starlette.staticfiles import StaticFiles
from werkzeug.utils import secure_filename

from HDT.config.prod_settings import PLAYWRIGHT_MCP_FILE_PATH, MOBILE_MCP_FILE_PATH

# 创建Flask对象
app_server = Flask(__name__)
# 加载配置
# app_server.config.from_pyfile('HDT/config/dev_settings.py')
app_server.config.from_pyfile('HDT/config/prod_settings.py')
# print(app_server.config)
# 跨域处理，前后端对接时才会用到，提前在这里处理了
CORS(app_server, resources=r'/*', max_age=86400)  # 缓存预检结果24小时
# 数据库连接
database = SQLAlchemy()
database.init_app(app_server)

# 初始化JWT
jwt = JWTManager()
jwt.init_app(app_server)

# ========== 核心配置（根据你的实际路径修改） ==========
# ================= 静态文件映射（G 盘）=================
@app_server.route("/tmp/playwright_mcp/<filename>")
def serve_playwright_img(filename):
    return send_from_directory("E:/tmp/playwright_mcp", filename)

@app_server.route("/tmp/mobile_mcp/<filename>")
def serve_mobile_img(filename):
    return send_from_directory("E:/tmp/mobile_mcp", filename)
# ======================================================
# 允许访问的图片格式
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'bmp']


# ========== 工具函数 ==========
def allowed_file(filename):
    """验证文件格式是否合法"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def decode_chinese_filename(encoded_filename):
    """解码 URL 编码的中文文件名"""
    try:
        decoded_name = urllib.parse.unquote(encoded_filename)
        decoded_name = decoded_name.encode('utf-8').decode('utf-8')
        # 修复 secure_filename 过滤中文的问题
        safe_name = secure_filename(decoded_name)
        safe_name = decoded_name if decoded_name else safe_name
        return safe_name
    except Exception as e:
        app_server.logger.error(f"文件名解码失败：{e}")
        return encoded_filename


# ========== 接口 1：显式指定目录访问图片 ==========
# 访问示例：
# Playwright 目录：http://localhost:5000/tmp/playwright_mcp/1769775218_点击注册按钮.png
# Mobile 目录：http://localhost:5000/tmp/mobile_mcp/1769775218_点击注册按钮.png
@app_server.route('/tmp/<dir_type>/<path:filename>', methods=['GET'])
def get_image_by_dir(dir_type, filename):
    """根据目录标识（playwright/mobile）访问指定目录的图片"""
    # 1. 映射目录标识到实际路径

    if dir_type == "playwright_mcp":
        target_dir = PLAYWRIGHT_MCP_FILE_PATH
    elif dir_type == "mobile_mcp":
        target_dir = MOBILE_MCP_FILE_PATH
    else:
        abort(400, description=f"无效的目录类型，仅支持：{PLAYWRIGHT_MCP_FILE_PATH}和{MOBILE_MCP_FILE_PATH}")

    print("target_dir:", target_dir)
    # 2. 解码中文文件名
    decoded_filename = decode_chinese_filename(filename)
    app_server.logger.info(f"解码后的文件名：{decoded_filename}（目标目录：{target_dir}）")

    # 3. 验证文件格式 + 检查文件是否存在
    if not allowed_file(decoded_filename):
        abort(400, description="不支持的文件格式，仅允许：png/jpg/jpeg/gif/bmp")

    file_path = os.path.join(target_dir, decoded_filename)
    file_path = file_path.replace('/', os.sep)
    if not os.path.exists(file_path):
        abort(404, description=f"图片 {decoded_filename} 在 {target_dir} 目录不存在")

    # 4. 返回图片（逻辑同方案1）
    try:
        response = send_from_directory(
            target_dir,
            os.path.basename(file_path),
            as_attachment=False
        )
        response.cache_control.no_cache = True
        response.cache_control.max_age = 0
        response.cache_control.public = False
        response.headers['Content-Disposition'] = f'inline; filename*=UTF-8\'\'{urllib.parse.quote(os.path.basename(file_path))}'
        return response
    except Exception as e:
        app_server.logger.error(f"返回图片失败：{e}")
        abort(500, description=f"服务器内部错误：{str(e)}")


if __name__ == '__main__':
    # 注册路由模块
    from HDT.controllers import ProjectController
    app_server.register_blueprint(ProjectController.module_route)  # 项目

    from HDT.controllers import TestDataTemplateController
    app_server.register_blueprint(TestDataTemplateController.module_route)  # 生成测试数据模板

    from HDT.controllers import DocumentController
    app_server.register_blueprint(DocumentController.module_route)  #  需求评审

    from HDT.controllers import ApiDocumentController
    app_server.register_blueprint(ApiDocumentController.module_route)  # 接口文档

    from HDT.controllers import TestCasesController
    app_server.register_blueprint(TestCasesController.module_route)  # UI测试用例

    from HDT.controllers import ApiTestCasesController
    app_server.register_blueprint(ApiTestCasesController.module_route)  # 接口测试用例

    from HDT.controllers import ApiTestCasesExecController
    app_server.register_blueprint(ApiTestCasesExecController.module_route)  # 接口测试用例执行

    from HDT.controllers import TestCasesExecController
    app_server.register_blueprint(TestCasesExecController.module_route)  # UI测试用例执行

    from HDT.controllers import PerformanceController
    app_server.register_blueprint(PerformanceController.module_route)  # 性能测试分析

    # debug=True：以debug的方式运行程序，当代码改动后，会自动更新服务
    # host="0.0.0.0"：设置服务的访问方式，0.0.0.0表示使用127.0.0.1、localhost和局域网IP访问
    # port=5000：指定端口号
    # app_server.run(debug=True, use_reloader=False, host="0.0.0.0", port=5001) # debug调试
    app_server.run(debug=True, host="0.0.0.0", port=5001)
