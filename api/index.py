# Railway Serverless 入口点
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 导入Flask应用
from app import app

# Railway要求导出名为"application"的变量
application = app