from flask import Flask, app
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from flask_mail import Mail

mail = Mail()

from config import Config
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'login'


socketIO = SocketIO()


# def create_app(config_class = Config):
def create_app(__name__):
    app = Flask(__name__)
    app.config.from_object(Config)

    mail.init_app(app)


    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    socketIO.init_app(app)

    from .routes import init_routes
    init_routes(app)

    with app.app_context():
        db.create_all()


    return app