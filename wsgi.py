# PythonAnywhere WSGI配置文件
import os
import sys

# 添加项目目录到Python路径
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'production')

# 导入应用
from app import create_app
application = create_app('production')

if __name__ == "__main__":
    application.run()
