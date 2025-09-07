
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'una-clave-muy-secreta')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Credenciales del usuario administrador por defecto
    DEFAULT_ADMIN_USERNAME = os.environ.get('DEFAULT_ADMIN_USERNAME', 'admin')
    DEFAULT_ADMIN_PASSWORD = os.environ.get('DEFAULT_ADMIN_PASSWORD')
    
    # Configuracion de CORS
    _origins_str = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000,https://m-s-system.onrender.com')
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in _origins_str.split(',')]

