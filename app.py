import logging
import os
from flask import Flask, request, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel, gettext as _
from config import get_config

db = SQLAlchemy()
login_manager = LoginManager()
babel = Babel()

def create_app(config_name=None):
    app = Flask(__name__)
    config_obj = get_config(config_name)
    app.config.from_object(config_obj)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Initialize Babel
    babel.init_app(app)

    @babel.localeselector
    def get_locale():
        # Try to get language from session, default to English
        return session.get('language', 'en')

    @babel.timezoneselector
    def get_timezone():
        return 'UTC'

    # Configure logging system
    setup_logging(app, config_obj)

    # Configure user loader function
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.query.get(int(user_id))

    # Request hooks for logging
    @app.before_request
    def before_request():
        g.start_time = __import__('time').time()

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = __import__('time').time() - g.start_time
            # record low requst
            if duration > 1.0:  # request that is over 1 second
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
    """ Equip app system"""
    # make sure log existed
    log_dir = os.path.join(app.root_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # decide log level: use config_obj first, then use app.config
    log_level = None
    if config_obj is not None:
        try:
            log_level = getattr(config_obj, 'LOG_LEVEL', None)
        except Exception:
            log_level = None
    if not log_level:
        # app.config usually store the settings from config_obj usually saved in app.config
        log_level = app.config.get('LOG_LEVEL', 'INFO')

    app.logger.setLevel(getattr(logging, str(log_level).upper(), logging.INFO))

    # remove default handler
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)

    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # file handler - all logs
    file_handler = logging.FileHandler(os.path.join(log_dir, 'app.log'))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    # error log file handler
    error_file_handler = logging.FileHandler(os.path.join(log_dir, 'error.log'))
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    app.logger.addHandler(error_file_handler)

    # console handler - only show warning and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)

    # configure specific module logger
    loggers = {
        'auth': logging.getLogger('auth'),
        'film': logging.getLogger('film'),
        'interaction': logging.getLogger('interaction'),
        'recommendation': logging.getLogger('recommendation')
    }

    for name, logger in loggers.items():
        logger.setLevel(logging.INFO)
        # avoid duplicate handler
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(error_file_handler)

    app.logger.info('Logging system initialized')

# create app based on environment variable
config_name = os.environ.get('FLASK_ENV') or 'development'

if __name__ == "__main__":
    app = create_app(config_name)
    app.run(debug=app.config['DEBUG'])
