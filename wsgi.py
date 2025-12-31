# PythonAnywhere WSGI configuration
import os
import sys

from app import create_app

# add to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# set Environment variables
os.environ.setdefault('FLASK_ENV', 'production')
application = create_app('production')

if __name__ == "__main__":
    application.run()
