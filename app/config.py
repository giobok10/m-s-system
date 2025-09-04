
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'una-clave-muy-secreta')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:////app/instance/restaurant.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Credenciales del usuario administrador por defecto
    DEFAULT_ADMIN_USERNAME = os.environ.get('DEFAULT_ADMIN_USERNAME', 'admin')
    DEFAULT_ADMIN_PASSWORD = os.environ.get('DEFAULT_ADMIN_PASSWORD', '4dM1n-#123-SyM')
    
    # Configuracion de CORS
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:5000')

