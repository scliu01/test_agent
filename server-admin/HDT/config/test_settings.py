# 开发环境--需要的配置，格式为mysql+pymysql://账号:密码@连接地址/数据库名称?连接参数
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root1234@127.0.0.1:3306/hc_ai_agent?charset=utf8'
SQLALCHEMY_TRACK_MODIFICATIONS = True
# 打印sql语句
SQLALCHEMY_ECHO = True
# 密钥，不要让别人知道
SECRET_KEY = "1234567812345678"