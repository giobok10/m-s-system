from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_moment import Moment
from .config import Config
from zoneinfo import ZoneInfo
import json

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
moment = Moment()

def format_datetime_local(dt_utc, format="%d/%m/%Y %H:%M"):
    if dt_utc is None:
        return ""
    guatemala_tz = ZoneInfo("America/Guatemala")
    dt_local = dt_utc.replace(tzinfo=ZoneInfo("UTC")).astimezone(guatemala_tz)
    return dt_local.strftime(format)

def parse_extras_filter(extras_json):
    """Jinja filter to parse a JSON string of extras and return a readable string with quantities."""
    if not extras_json:
        return ""
    try:
        extras_list = json.loads(extras_json)
        if not isinstance(extras_list, list) or not extras_list:
            return ""
        
        parts = []
        for extra in extras_list:
            if isinstance(extra, dict) and 'name' in extra and 'quantity' in extra:
                parts.append(f"{extra['name']} (x{extra['quantity']})")
        
        return ', '.join(parts)
    except (json.JSONDecodeError, TypeError):
        return extras_json

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Register custom Jinja filters
    app.jinja_env.filters['datetime_local'] = format_datetime_local
    app.jinja_env.filters['parse_extras'] = parse_extras_filter

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins=app.config['CORS_ALLOWED_ORIGINS'], ping_timeout=20, ping_interval=10)
    moment.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Import models
    from app.models import User
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.waiter_routes import waiter_bp
    from app.routes.cook_routes import cook_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(waiter_bp, url_prefix='/waiter')
    app.register_blueprint(cook_bp, url_prefix='/cook')
    
    # Register socket events
    from app.sockets.order_events import register_socket_events
    register_socket_events(socketio)
    
    # Create tables and default admin user
    with app.app_context():
        db.create_all()
        create_default_admin(app)
    
    return app

def create_default_admin(app):
    from app.models import User
    from werkzeug.security import generate_password_hash
    
    # Check if admin exists
    admin = User.query.filter_by(username=app.config['DEFAULT_ADMIN_USERNAME']).first()
    if not admin:
        admin_user = User(
            username=app.config['DEFAULT_ADMIN_USERNAME'],
            password_hash=generate_password_hash(app.config['DEFAULT_ADMIN_PASSWORD']),
            role='admin',
            full_name='Administrador'
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f"Default admin user created: {app.config['DEFAULT_ADMIN_USERNAME']}/{app.config['DEFAULT_ADMIN_PASSWORD']}")
