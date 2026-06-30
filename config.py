import os

from pathlib import Path

import app


class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-development-secret-key')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') # Use an App Password from Google, never your actual password!

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER = 'noreply.zwipionline@gmail.com'
    
    DEBUG = os.environ.get('FLASK_DEBUG','False').lower()in ('true','1','t')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS','*')

    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URL','sqlite:///zwipiOnline.db') or \
        'sqlite:///' + str(Path(__file__).parent / 'app.db')
    
    db_url = os.environ.get('DATABASE_URL','sqlite:///zwipiOnline.db')
    if  db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = False
