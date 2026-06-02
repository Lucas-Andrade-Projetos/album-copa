import os
from flask import Flask
from flask_login import LoginManager


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile("../config.py")

    os.makedirs(app.instance_path, exist_ok=True)

    from . import database
    database.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para continuar."
    login_manager.login_message_category = "error"
    login_manager.init_app(app)

    from .auth import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    from . import auth, stickers
    app.register_blueprint(auth.bp)
    app.register_blueprint(stickers.bp)

    return app
