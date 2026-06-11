from functools import wraps
from datetime import date
from flask import Blueprint, render_template, jsonify, request, abort
from flask_login import login_required, current_user
from .database import get_db

bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@bp.route("/")
@login_required
@admin_required
def index():
    db = get_db()

    usuarios = db.execute("SELECT id, username FROM users ORDER BY username").fetchall()
    stickers = db.execute(
        "SELECT id, number, player_name, rarity FROM stickers ORDER BY number"
    ).fetchall()

    total_stickers = len(stickers)
    stats = []
    for u in usuarios:
        obtidas = db.execute(
            "SELECT COUNT(*) as n FROM user_stickers WHERE user_id = ?", (u["id"],)
        ).fetchone()["n"]
        percent = round((obtidas / total_stickers) * 100) if total_stickers > 0 else 0
        pacotes_hoje = db.execute(
            "SELECT COUNT(*) as n FROM pack_openings WHERE user_id = ? AND date(opened_at) = ?",
            (u["id"], date.today().isoformat()),
        ).fetchone()["n"]
        stats.append({
            "id":           u["id"],
            "username":     u["username"],
            "obtidas":      obtidas,
            "total":        total_stickers,
            "percent":      percent,
            "pacotes_hoje": pacotes_hoje,
        })

    return render_template("admin.html", stats=stats, stickers=stickers, usuarios=usuarios)


@bp.route("/api/force-sticker", methods=["POST"])
@login_required
@admin_required
def force_sticker():
    data       = request.get_json()
    user_id    = data.get("user_id")
    sticker_id = data.get("sticker_id")

    if not user_id or not sticker_id:
        return jsonify({"success": False, "error": "user_id e sticker_id são obrigatórios"}), 400

    db = get_db()
    db.execute(
        "INSERT INTO admin_overrides (target_user_id, sticker_id) VALUES (?, ?)",
        (user_id, sticker_id),
    )
    db.commit()

    sticker = db.execute(
        "SELECT player_name FROM stickers WHERE id = ?", (sticker_id,)
    ).fetchone()
    usuario = db.execute(
        "SELECT username FROM users WHERE id = ?", (user_id,)
    ).fetchone()

    return jsonify({
        "success": True,
        "message": f"'{sticker['player_name']}' será incluída no próximo pacote de {usuario['username']}.",
    })


@bp.route("/api/grant-sticker", methods=["POST"])
@login_required
@admin_required
def grant_sticker():
    data       = request.get_json()
    user_id    = data.get("user_id")
    sticker_id = data.get("sticker_id")

    if not user_id or not sticker_id:
        return jsonify({"success": False, "error": "user_id e sticker_id são obrigatórios"}), 400

    db = get_db()
    existing = db.execute(
        "SELECT id FROM user_stickers WHERE user_id = ? AND sticker_id = ?",
        (user_id, sticker_id),
    ).fetchone()

    if existing:
        db.execute(
            "UPDATE user_stickers SET quantity = quantity + 1 WHERE id = ?",
            (existing["id"],),
        )
    else:
        db.execute(
            "INSERT INTO user_stickers (user_id, sticker_id, quantity) VALUES (?, ?, 1)",
            (user_id, sticker_id),
        )
    db.commit()

    sticker = db.execute("SELECT player_name FROM stickers WHERE id = ?", (sticker_id,)).fetchone()
    usuario = db.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()

    return jsonify({
        "success": True,
        "message": f"'{sticker['player_name']}' concedida diretamente a {usuario['username']}.",
    })


@bp.route("/api/reset-daily", methods=["POST"])
@login_required
@admin_required
def reset_daily():
    data    = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"success": False, "error": "user_id é obrigatório"}), 400

    db = get_db()
    db.execute(
        "DELETE FROM pack_openings WHERE user_id = ? AND date(opened_at) = ?",
        (user_id, date.today().isoformat()),
    )
    db.commit()

    usuario = db.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
    return jsonify({
        "success": True,
        "message": f"Limite diário de {usuario['username']} resetado.",
    })


@bp.route("/api/clear-album", methods=["POST"])
@login_required
@admin_required
def clear_album():
    data    = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"success": False, "error": "user_id é obrigatório"}), 400

    db = get_db()
    db.execute("DELETE FROM user_stickers WHERE user_id = ?", (user_id,))
    db.commit()

    usuario = db.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
    return jsonify({
        "success": True,
        "message": f"Álbum de {usuario['username']} limpo.",
    })
