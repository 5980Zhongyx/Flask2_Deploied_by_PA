import logging
import os
from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import get_config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name=None):
    app = Flask(__name__)
    config_obj = get_config(config_name)
    app.config.from_object(config_obj)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # 配置日志系统
    setup_logging(app, config_obj)

    # 配置用户加载函数
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.query.get(int(user_id))

    # 请求前后的钩子，用于日志记录
    @app.before_request
    def before_request():
        g.start_time = __import__('time').time()

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = __import__('time').time() - g.start_time
            # 记录慢请求
            if duration > 1.0:  # 超过1秒的请求
                app.logger.warning('.3f'
                                 f'user_agent={request.headers.get("User-Agent", "Unknown")[:100]}')

        return response

    from routes.auth_routes import auth_bp
    from routes.film_routes import film_bp
    from routes.interaction_routes import interaction_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(film_bp)
    app.register_blueprint(interaction_bp)

    with app.app_context():
        db.create_all()

    return app

def setup_logging(app, config_obj=None):
    """配置应用日志系统"""
    # 确保日志目录存在
    log_dir = os.path.join(app.root_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # 决定日志级别：优先使用传入的 config_obj，其次使用 app.config
    log_level = None
    if config_obj is not None:
        try:
            log_level = getattr(config_obj, 'LOG_LEVEL', None)
        except Exception:
            log_level = None
    if not log_level:
        # app.config 里通常保存了从 config_obj 导入的设置
        log_level = app.config.get('LOG_LEVEL', 'INFO')

    app.logger.setLevel(getattr(logging, str(log_level).upper(), logging.INFO))

    # 移除默认处理器
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)

    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 文件处理器 - 所有日志
    file_handler = logging.FileHandler(os.path.join(log_dir, 'app.log'))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    # 错误日志文件处理器
    error_file_handler = logging.FileHandler(os.path.join(log_dir, 'error.log'))
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    app.logger.addHandler(error_file_handler)

    # 控制台处理器 - 只显示警告及以上级别
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)

    # 配置特定模块的日志器
    loggers = {
        'auth': logging.getLogger('auth'),
        'film': logging.getLogger('film'),
        'interaction': logging.getLogger('interaction'),
        'recommendation': logging.getLogger('recommendation')
    }

    for name, logger in loggers.items():
        logger.setLevel(logging.INFO)
        # 避免重复添加处理器
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(error_file_handler)

    app.logger.info('Logging system initialized')

# 根据环境变量创建应用
config_name = os.environ.get('FLASK_ENV') or 'development'

if __name__ == "__main__":
    app = create_app(config_name)
    app.run(debug=app.config['DEBUG'])
