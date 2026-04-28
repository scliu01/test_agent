# 开发环境--需要的配置，格式为mysql+pymysql://账号:密码@连接地址/数据库名称?连接参数
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:agent.123.com@www.agentscl.cn:3306/test_agent_mysql?charset=utf8mb4'
SQLALCHEMY_TRACK_MODIFICATIONS = True
# 打印sql语句
SQLALCHEMY_ECHO = True
# 密钥，不要让别人知道
SECRET_KEY = "1234567812345678"

# JWT_SECRET_KEY鉴权
JWT_SECRET_KEY = "jwt-secret-key-change-in-production-12345678" # 秘钥
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 默认1小时
JWT_REFRESH_TOKEN_EXPIRES = 86400 * 30  # 默认30天

# mcp服务器地址
PLAYWRIGHT_MCP_SERVER = "http://localhost:8931/sse"
MOBILE_MCP_SERVER = "http://127.0.0.1:8932/mcp"

# 要和mcp服务启动的目录一致，例如，npx -y @playwright/mcp@latest --isolated --browser chromium --port 8931 --viewport-size "1920,1080"  --host 0.0.0.0 --output-dir ~/tmp/playwright_mcp
# 要最后的 --output-dir ~/tmp/playwright_mcp
PLAYWRIGHT_MCP_FILE_PATH = r"http://www.agentscl.cn:5001/tmp/playwright_mcp"
MOBILE_MCP_FILE_PATH = r"http://www.agentscl.cn:5001/tmp/mobile_mcp"