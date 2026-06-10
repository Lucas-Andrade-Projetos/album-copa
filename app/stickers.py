from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from .database import get_db

bp = Blueprint("stickers", __name__)


@bp.route("/album")
@login_required
def album():
    db = get_db()

    todas = db.execute(
        "SELECT id, number, player_name, country, rarity FROM stickers ORDER BY number"
    ).fetchall()

    possuidas = db.execute(
        "SELECT sticker_id, quantity FROM user_stickers WHERE user_id = ?",
        (current_user.id,),
    ).fetchall()

    mapa_possuidas = {row["sticker_id"]: row["quantity"] for row in possuidas}

    total = len(todas)
    obtidas = len(mapa_possuidas)
    percent = round((obtidas / total) * 100) if total > 0 else 0

    return render_template(
        "album.html",
        stickers=todas,
        owned=mapa_possuidas,
        total=total,
        obtidas=obtidas,
        percent=percent,
    )
