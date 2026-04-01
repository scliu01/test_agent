# 开发环境--需要的配置，格式为mysql+pymysql://账号:密码@连接地址/数据库名称?连接参数
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@127.0.0.1:3306/test_agent_mysql?charset=utf8mb4'
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@8.162.0.206:3306/test_agent_mysql?charset=utf8mb4'
# 是否追踪数据库的修改
SQLALCHEMY_TRACK_MODIFICATIONS = True
# 打印sql语句
SQLALCHEMY_ECHO = True
# 密钥，不要让别人知道
SECRET_KEY = "1234567812345678"

# mcp服务器地址
PLAYWRIGHT_MCP_SERVER = "http://localhost:8931/sse"
MOBILE_MCP_SERVER = "http://127.0.0.1:8932/mcp"

# 要和mcp服务启动的目录一致，例如，npx -y @playwright/mcp@latest --isolated --browser chromium --port 8931 --viewport-size "1920,1080"  --host 0.0.0.0 --output-dir ~/tmp/playwright_mcp
# 要最后的 --output-dir ~/tmp/playwright_mcp
PLAYWRIGHT_MCP_FILE_PATH = r"/tmp/playwright_mcp"
MOBILE_MCP_FILE_PATH = r"/tmp/mobile_mcp"