import os
from datetime import timedelta
from flask import Flask, session, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)

    # Security & App Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'c18e9f2a9d8042459c381d599bdfca67_secure_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Session Security (20-minute inactivity timeout)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS

    # Initialize Extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access your notes dashboard.'
    login_manager.login_message_category = 'info'

    # Enforce session permanence & inactivity timeout on each request
    @app.before_request
    def enforce_session_lifetime():
        session.permanent = True
        session.modified = True

    # Error Handlers
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return render_template(
            'base.html',
            rate_limit_error=f"Too many requests. Rate limit exceeded: {e.description}"
        ), 429

    @app.errorhandler(403)
    def forbidden_handler(e):
        return render_template(
            'base.html',
            general_error="Access forbidden. You are not authorized to perform this action."
        ), 403

    @app.errorhandler(404)
    def not_found_handler(e):
        return render_template(
            'base.html',
            general_error="The requested page could not be found."
        ), 404

    # Register Blueprints
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    return app
