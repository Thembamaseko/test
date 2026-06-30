import os
from pathlib import Path


class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-development-secret-key')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Use an App Password from Google, never your actual password!

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER = 'noreply.zwipionline@gmail.com'

    SQLALCHEMY_DATABASE_URI = "postgresql://zwipi_5gal_user:HkEctDmV1UOrBovPlQ6TNbPnt8klPpI4@dpg-d91m3n3eo5us739bhhdg-a.oregon-postgres.render.com/zwipi_5gal"

    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    