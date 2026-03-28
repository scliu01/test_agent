# 1. 导入
from crypt import methods

from flask import Flask, request

# 2. 创建Flask对象
app = Flask(__name__)


# 3. 创建一个get请求
@app.route('/get_demo')
def get_demo():
    return 'get_demo'


# 创建一个get请求，响应一段HTML代码。
@app.route('/html_demo')
def html_demo():
    return '''
    <html>
        <head>
            <title>HTML</title>
        </head>
        <body>
            <h1>Hello World!</h1>
        </body>
    </html>
    '''


# 创建一个get请求，返回一段JSON数据。
@app.route('/json_demo')
def json_demo():
    return {'name': '张三', 'age': 18}


@app.route('/post_demo', methods=['POST'])
def post_demo():
    print(request.form)
    return 'post_demo'


if __name__ == '__main__':
    # 4. 启动服务器
    # 以调试的模式来运行服务器，调试模式下，每次代码修改后，服务器都会自动重启
    # host='0.0.0.0'：支持不同的ip访问，localhost:5001、局域网ip:5001、127.0.0.1:5001
    app.run(debug=True, host='0.0.0.0', port=5002)
