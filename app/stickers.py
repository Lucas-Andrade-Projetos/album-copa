from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from .database import get_db
from .utils import get_packs_opened_today, draw_stickers, award_stickers, record_pack_opening
from flask import current_app

bp = Blueprint("stickers", __name__)


@bp.route("/pack")
@login_required
def pack():
    db = get_db()
    packs_per_day = current_app.config["PACKS_PER_DAY"]
    abertos_hoje  = get_packs_opened_today(current_user.id, db)
    restantes     = max(0, packs_per_day - abertos_hoje)
    return render_template("open_pack.html", packs_remaining=restantes)


@bp.route("/api/album/status")
@login_required
def album_status():
    db = get_db()
    total = db.execute("SELECT COUNT(*) as n FROM stickers").fetchone()["n"]
    obtidas = db.execute(
        "SELECT COUNT(*) as n FROM user_stickers WHERE user_id = ?",
        (current_user.id,),
    ).fetchone()["n"]
    duplicatas = db.execute(
        "SELECT SUM(quantity - 1) as n FROM user_stickers WHERE user_id = ? AND quantity > 1",
        (current_user.id,),
    ).fetchone()["n"] or 0
    percent = round((obtidas / total) * 100) if total > 0 else 0
    return jsonify({
        "owned":       obtidas,
        "total":       total,
        "percent":     percent,
        "complete":    obtidas >= total,
        "duplicates":  duplicatas,
    })


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


@bp.route("/api/pack/remaining")
@login_required
def pack_remaining():
    db = get_db()
    packs_per_day = current_app.config["PACKS_PER_DAY"]
    abertos_hoje  = get_packs_opened_today(current_user.id, db)
    restantes     = max(0, packs_per_day - abertos_hoje)
    return jsonify({"packs_remaining": restantes, "packs_per_day": packs_per_day})


@bp.route("/leaderboard")
@login_required
def leaderboard():
    db = get_db()
    total = db.execute("SELECT COUNT(*) as n FROM stickers").fetchone()["n"]

    rows = db.execute(
        "SELECT u.id, u.username, COUNT(us.sticker_id) as obtidas"
        " FROM users u"
        " LEFT JOIN user_stickers us ON us.user_id = u.id"
        " WHERE u.is_admin = 0"
        " GROUP BY u.id"
        " ORDER BY obtidas DESC, u.username ASC",
    ).fetchall()

    ranking = []
    for pos, row in enumerate(rows, start=1):
        percent = round((row["obtidas"] / total) * 100) if total > 0 else 0
        ranking.append({
            "pos":      pos,
            "username": row["username"],
            "obtidas":  row["obtidas"],
            "total":    total,
            "percent":  percent,
            "eu":       row["id"] == current_user.id,
        })

    return render_template("leaderboard.html", ranking=ranking)


@bp.route("/api/pack/open", methods=["POST"])
@login_required
def pack_open():
    db = get_db()
    packs_per_day    = current_app.config["PACKS_PER_DAY"]
    stickers_per_pack = current_app.config["STICKERS_PER_PACK"]

    abertos_hoje = get_packs_opened_today(current_user.id, db)
    if abertos_hoje >= packs_per_day:
        restantes = max(0, packs_per_day - abertos_hoje)
        return jsonify({
            "success": False,
            "error": "Limite diário atingido. Volte amanhã!",
            "packs_remaining": restantes,
        }), 429

    possuidas_antes = db.execute(
        "SELECT sticker_id FROM user_stickers WHERE user_id = ?",
        (current_user.id,),
    ).fetchall()
    ids_antes = {r["sticker_id"] for r in possuidas_antes}

    sorteadas = draw_stickers(db, stickers_per_pack, user_id=current_user.id)

    ids_sorteados = [s["id"] for s in sorteadas]
    award_stickers(current_user.id, ids_sorteados, db)
    record_pack_opening(current_user.id, ids_sorteados, db)

    resultado = []
    vistos_neste_pacote = set()
    for s in sorteadas:
        is_new = s["id"] not in ids_antes and s["id"] not in vistos_neste_pacote
        vistos_neste_pacote.add(s["id"])
        resultado.append({
            "id":          s["id"],
            "player_name": s["player_name"],
            "country":     s["country"],
            "rarity":      s["rarity"],
            "is_new":      is_new,
        })

    restantes = max(0, packs_per_day - abertos_hoje - 1)
    return jsonify({
        "success":         True,
        "stickers":        resultado,
        "packs_remaining": restantes,
    })
