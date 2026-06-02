from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .database import get_db

bp = Blueprint("auth", __name__)


class User(UserMixin):
    def __init__(self, id, username, is_admin):
        self.id = id
        self.username = username
        self.is_admin = bool(is_admin)

    @staticmethod
    def get(user_id):
        db = get_db()
        row = db.execute("SELECT id, username, is_admin FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            return None
        return User(row["id"], row["username"], row["is_admin"])

    @staticmethod
    def get_by_username(username):
        db = get_db()
        row = db.execute(
            "SELECT id, username, password, is_admin FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        return row


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("stickers.album"))
    return redirect(url_for("auth.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("stickers.album"))

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        error = None

        row = User.get_by_username(username)

        if row is None:
            error = "Usuário não encontrado."
        elif not check_password_hash(row["password"], password):
            error = "Senha incorreta."

        if error is None:
            user = User(row["id"], row["username"], row["is_admin"])
            login_user(user)
            return redirect(url_for("stickers.album"))

        flash(error, "error")

    return render_template("login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("stickers.album"))

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        confirm  = request.form["confirm"]
        error = None

        if not username:
            error = "Nome de usuário é obrigatório."
        elif len(username) < 3:
            error = "Nome de usuário deve ter pelo menos 3 caracteres."
        elif not password:
            error = "Senha é obrigatória."
        elif len(password) < 6:
            error = "Senha deve ter pelo menos 6 caracteres."
        elif password != confirm:
            error = "As senhas não coincidem."
        elif User.get_by_username(username) is not None:
            error = f"O usuário '{username}' já existe."

        if error is None:
            db = get_db()
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            db.commit()
            flash("Conta criada! Faça login.", "success")
            return redirect(url_for("auth.login"))

        flash(error, "error")

    return render_template("register.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
