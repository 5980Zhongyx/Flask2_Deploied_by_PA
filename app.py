import logging
import os
from flask import Flask, request, g, session
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel, gettext as _
from datetime import datetime, timedelta
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

    # Return JSON 401 for AJAX/Fetch requests when unauthorized instead of HTML redirect
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        from flask import jsonify, request, redirect, url_for
        # Treat fetch/XHR requests as API calls and return 401 JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.accept_json:
            return jsonify({"success": False, "message": "Authentication required"}), 401
        # otherwise redirect to login page (preserve next)
        return redirect(url_for('auth.login', next=request.url))

    # Initialize Babel
    babel.init_app(app)

    # Jinja helper to check for static file existence (used to fallback posters)
    app.jinja_env.globals['static_file_exists'] = lambda path: os.path.exists(os.path.join(app.static_folder, path))

    # Locale selector: support different Flask-Babel versions
    def _get_locale():
        return session.get('language', 'en')

    # Register locale selector based on available API
    try:
        # Newer Flask-Babel versions support decorator registration
        if hasattr(babel, 'localeselector'):
            babel.localeselector(_get_locale)
        elif hasattr(babel, 'locale_selector_func'):
            # alternative API
            babel.locale_selector_func = _get_locale
        else:
            # fallback: set default locale from session on each request
            app.config.setdefault('BABEL_DEFAULT_LOCALE', 'en')
    except Exception:
        app.config.setdefault('BABEL_DEFAULT_LOCALE', 'en')

    # Timezone selector (best-effort)
    def _get_timezone():
        return 'UTC'
    try:
        if hasattr(babel, 'timezoneselector'):
            babel.timezoneselector(_get_timezone)
        elif hasattr(babel, 'timezone_selector_func'):
            babel.timezone_selector_func = _get_timezone
    except Exception:
        pass

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
        # Configure session security settings
        session.permanent = True

        # Clean up expired sessions periodically (every 100 requests)
        if not hasattr(g, 'session_cleanup_counter'):
            g.session_cleanup_counter = 0
        g.session_cleanup_counter += 1

        if g.session_cleanup_counter % 100 == 0:
            cleanup_expired_sessions(app)

        # Additional security checks
        user_agent = request.headers.get('User-Agent', '')
        if not user_agent or len(user_agent) < 10:
            # Suspicious request - log it
            app.logger.warning(f"Suspicious request from {request.remote_addr}: missing or short User-Agent")

        # Check for potential XSS attempts in common headers
        suspicious_headers = ['Referer', 'X-Forwarded-For']
        for header in suspicious_headers:
            value = request.headers.get(header, '')
            if value and ('<' in value or '>' in value or 'javascript:' in value.lower()):
                app.logger.warning(f"Potential XSS attempt in {header}: {value[:100]}...")

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = __import__('time').time() - g.start_time
            # record low requst
            if duration > 1.0:  # request that is over 1 second
                app.logger.warning('.3f'
                                 f'user_agent={request.headers.get("User-Agent", "Unknown")[:100]}')

        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Content Security Policy for additional protection
        csp = (
            "default-src 'self'; "
            # allow scripts from our CDN provider
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            # allow styles including inline styles and known CDNs (Google Fonts, Cloudflare)
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
            # images from self, data URIs and https sources (posters may be remote)
            "img-src 'self' data: https:; "
            # fonts from self, data and common font CDNs (Google Fonts, Cloudflare)
            "font-src 'self' data: https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "connect-src 'self';"
        )
        response.headers['Content-Security-Policy'] = csp

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

def cleanup_expired_sessions(app):
    """Clean up expired sessions from database"""
    try:
        # This is a simple cleanup - in production you might want more sophisticated session management
        # For now, we'll just log that cleanup was attempted
        app.logger.info("Session cleanup triggered")
        # Note: Flask-Session with database backend would handle this automatically
        # For file-based sessions, you might need custom cleanup
    except Exception as e:
        app.logger.warning(f"Session cleanup failed: {e}")

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
