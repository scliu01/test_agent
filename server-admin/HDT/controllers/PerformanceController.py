import json
import re
import traceback
from datetime import datetime

from flask import Blueprint, request, Response, render_template_string
from openai import OpenAI

from HDT.models.projects import Project
from HDT.utils.ai_utils import load_prompt
from HDT.utils.resp_model import respModel
from app import app_server, database
from HDT.models.performance import Performance

# 路由名称
module_name = "performance"
# 路由对象，在app.py中加载到flask对象中
module_route = Blueprint(f"route_{module_name}", __name__)
# 数据库模块名称
module_model = Performance


# 查询所有数据
@module_route.route(f"/{module_name}/queryAll", methods=["GET"])
def queryAll():
    project_id = request.args.get("project_id")
    print(f"查询项目下的数据模板:{project_id}")
    with app_server.app_context():
        query = module_model.query
        if project_id:
            query = query.filter_by(project_id=project_id)
        return respModel().ok_resp_list(lst=query.all(), msg="查询成功")


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


from playwright.sync_api import sync_playwright
import cv2
import numpy as np
import base64
import uuid


def webpage_as_image(url, color_threshold=10, sample_height=10):
    with sync_playwright() as p:
        # 启动浏览器（这里使用Chromium，也可以选择firefox或webkit）
        browser = p.chromium.launch(headless=True)  # headless=True 表示无头模式
        page = browser.new_page()  # 创建新页面
        page.set_viewport_size({"width": 1920, "height": 5000})  # 设置大视口
        page.goto(url, timeout=60000)  # 访问指定网址
        page.wait_for_load_state("networkidle")  # 最终等待确保所有资源加载
        page.wait_for_timeout(2000)
        screenshot_bytes = page.screenshot(full_page=True, type="jpeg")
        browser.close()  # 关闭浏览器
    original_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')

    # 裁剪顶部+底部纯色区域
    try:
        # 解码为OpenCV图像
        img_array = np.frombuffer(screenshot_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            print("无法解码截图")
            return original_base64

        height, width = img.shape[:2]
        top_y = 0  # 顶部有效区域起始行
        bottom_y = height - 1  # 底部有效区域结束行

        # ========== 第一步：检测并裁剪顶部纯色区域 ==========
        # 采样顶部sample_height行的平均颜色
        top_sample = img[:sample_height, :]
        top_avg_color = np.mean(top_sample, axis=(0, 1))
        # 从上往下找第一个颜色差异超过阈值的行
        for y in range(0, height):
            row = img[y, :]
            diff = np.mean(np.abs(row - top_avg_color))
            if diff > color_threshold:
                top_y = y  # 确定顶部有效区域起始位置
                break

        # ========== 第二步：检测并裁剪底部纯色区域 ==========
        # 采样底部sample_height行的平均颜色
        bottom_sample = img[-sample_height:, :]
        bottom_avg_color = np.mean(bottom_sample, axis=(0, 1))
        # 从下往上找第一个颜色差异超过阈值的行
        for y in range(height - 1, -1, -1):
            row = img[y, :]
            diff = np.mean(np.abs(row - bottom_avg_color))
            if diff > color_threshold:
                bottom_y = y  # 确定底部有效区域结束位置
                break

        # ========== 第三步：裁剪有效区域（顶部→底部） ==========
        cropped_img = img[top_y:bottom_y + 1, :]

        # 编码为Base64返回
        _, buffer = cv2.imencode('.jpg', cropped_img)
        cropped_base64 = base64.b64encode(buffer).decode('utf-8')

        print(f"裁剪完成：原始尺寸{height}x{width} → 裁剪后{cropped_img.shape[0]}x{cropped_img.shape[1]}")
        return cropped_base64

    except Exception as e:
        print(f"裁剪过程中出错: {str(e)}")
        return original_base64  # 出错时返回原始Base64


@module_route.route(f"/{module_name}/process_with_ai_stream", methods=["POST"])
def process_with_ai_stream():
    """ 使用AI处理生成测试数据 """
    try:
        # 打印接收的参数
        print(f"接收到的参数: {request.json}")
        # 获取请求参数
        # 获取请求参数
        project_id = request.json.get("project_id")
        start_time = request.json.get("start_time")
        end_time = request.json.get("end_time")
        import json
        serverConfigs = json.loads(request.json.get("configs"))

        if not project_id:
            return respModel.error_resp(msg="缺少必填参数: project_id")

        # 根据project_id查询项目配置的AI模型地址
        with app_server.app_context():
            # 先从project表查询model字段
            project = Project.query.filter_by(id=project_id).first()
            if not project:
                return respModel.error_resp(msg=f"项目不存在: {project_id}")
            # 打印project
            print(f"项目: {str(project.to_dict())}")

            if not project.llm_url or not project.llm_key or not project.llm_model:
                return respModel.error_resp(msg=f"项目 {project_id} 未配置AI模型地址")
            # 加载图片处理提示词
            image_parse_prompt = load_prompt("../prompts", "提示词-性能压测-监控数据提取.txt", {})
            print(f"生成的提示词 image_parse_prompt: {image_parse_prompt}")
            source_items = []
            for server in serverConfigs:
                # 提取 监控地址， 将时间调整
                source_url = render_template_string(server["source_url"], **{
                    "start_time": start_time,
                    "end_time": end_time
                })
                print(source_url)
                # 根据监控地址，打开浏览器截图保存
                base64_str = webpage_as_image(source_url)
                # 保存为文件
                filename = f"调试.jpg"
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(base64_str))
                # 将截图使用 LVM 进行数据提取
                from HDT.utils.ai_utils import ai_image
                result = ai_image(str(uuid.uuid4()), base64_str, project.lvm_key,
                                  project.lvm_url, project.lvm_model, image_parse_prompt, cache=False)
                source_items.append({
                    "title": server["name"],
                    "content": result
                })
            ai_prompt = load_prompt("../prompts", "提示词-性能分析.txt", {
                "source_items": source_items,
            })
            print(f"生成的提示词 ai_prompt: {ai_prompt}")
            # 使用OpenAI调用指定的大模型
            # 配置OpenAI客户端
            client = OpenAI(
                base_url=project.llm_url,
                # 注意：API密钥应通过环境变量或安全方式设置
                api_key=project.llm_key
            )
            # 调用大模型（流式）
            stream = client.chat.completions.create(
                model=project.llm_model,
                messages=[{"role": "user", "content": ai_prompt}],
                stream=True
            )

            # 设置流式响应
            def generate():
                try:
                    # 发送初始消息，yield将内容返回给前端, status是状态，start是开始状态，自定义设计
                    yield json.dumps({"status": "start", "content": "开始生成内容"}) + "\n"

                    full_content = ""
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            content = chunk.choices[0].delta.content
                            full_content += content
                            # 发送流式数据，yield将内容返回给前端
                            yield json.dumps({
                                "status": "streaming",  # streaming表示流式数据
                                "content": content,
                                "full_content": full_content
                            }) + "\n"
                    if not full_content.startswith("```json"):  # AI脑残返回处理
                        # 重新赋值：开头加 ```json，结尾加 ```
                        full_content = f"```json{full_content}```"
                    # 尝试解析JSON
                    try:
                        json_data = re.search(r"```json(.*?)```", full_content, re.DOTALL)
                        if json_data:
                            json_content = json_data.group(1)
                            parsed_data = json.loads(json_content)
                            yield json.dumps({
                                "status": "completed",  # completed表示完成
                                "data": parsed_data,
                                "raw_content": full_content
                            }) + "\n"
                        else:
                            yield json.dumps({
                                "status": "error",  # error表示错误
                                "message": "未找到JSON格式数据",
                                "raw_content": full_content
                            }) + "\n"

                    except json.JSONDecodeError as e:
                        yield json.dumps({
                            "status": "error",  # error表示错误
                            "message": f"JSON解析错误: {str(e)}",
                            "raw_content": full_content
                        }) + "\n"

                except Exception as e:
                    yield json.dumps({
                        "status": "error",  # error表示错误
                        "message": f"流式处理失败: {str(e)}"
                    }) + "\n"

            # 返回流式响应，需要导入 from flask import Response
            return Response(generate(), mimetype='text/plain', headers={'X-Accel-Buffering': 'no'})  # 禁用Nginx缓冲

    except Exception as e:
        traceback.print_exc()
        return respModel.error_resp(msg=f"AI处理失败: {str(e)}")
