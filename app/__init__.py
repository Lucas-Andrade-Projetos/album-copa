import os
from flask import Flask, render_template
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

    from . import auth, stickers, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(stickers.bp)
    app.register_blueprint(admin.bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("erro.html",
            codigo=404,
            titulo="Página não encontrada",
            descricao="O endereço que você tentou acessar não existe.",
        ), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("erro.html",
            codigo=403,
            titulo="Acesso negado",
            descricao="Você não tem permissão para acessar esta área.",
        ), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template("erro.html",
            codigo=500,
            titulo="Erro interno",
            descricao="Algo deu errado no servidor. Tente novamente em instantes.",
        ), 500

    return app
