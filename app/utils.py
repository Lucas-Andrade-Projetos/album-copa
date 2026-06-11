import json
import random
from datetime import date
from flask import current_app


RARITY_WEIGHTS = {
    "common":    70,
    "rare":      25,
    "legendary":  5,
}


def get_packs_opened_today(user_id, db):
    row = db.execute(
        "SELECT COUNT(*) as total FROM pack_openings"
        " WHERE user_id = ? AND date(opened_at) = ?",
        (user_id, date.today().isoformat()),
    ).fetchone()
    return row["total"]


def draw_stickers(db, n, user_id=None):
    # Consome overrides pendentes do admin (se houver)
    forcadas = []
    if user_id is not None:
        overrides = db.execute(
            "SELECT ao.id, s.id as sid, s.player_name, s.country, s.rarity"
            " FROM admin_overrides ao"
            " JOIN stickers s ON s.id = ao.sticker_id"
            " WHERE (ao.target_user_id = ? OR ao.target_user_id IS NULL)"
            "   AND ao.used = 0"
            " ORDER BY ao.id"
            " LIMIT ?",
            (user_id, n),
        ).fetchall()

        for row in overrides:
            forcadas.append({
                "id": row["sid"], "player_name": row["player_name"],
                "country": row["country"], "rarity": row["rarity"],
            })
            db.execute(
                "UPDATE admin_overrides SET used = 1 WHERE id = ?", (row["id"],)
            )
        db.commit()

    slots_restantes = n - len(forcadas)
    aleatorias = []
    if slots_restantes > 0:
        todas      = db.execute(
            "SELECT id, player_name, country, rarity FROM stickers"
        ).fetchall()
        population = list(todas)
        weights    = [RARITY_WEIGHTS.get(s["rarity"], 10) for s in population]
        aleatorias = [
            {"id": s["id"], "player_name": s["player_name"],
             "country": s["country"], "rarity": s["rarity"]}
            for s in random.choices(population, weights=weights, k=slots_restantes)
        ]

    return forcadas + aleatorias


def award_stickers(user_id, sticker_ids, db):
    for sid in sticker_ids:
        existing = db.execute(
            "SELECT id, quantity FROM user_stickers WHERE user_id = ? AND sticker_id = ?",
            (user_id, sid),
        ).fetchone()

        if existing:
            db.execute(
                "UPDATE user_stickers SET quantity = quantity + 1 WHERE id = ?",
                (existing["id"],),
            )
        else:
            db.execute(
                "INSERT INTO user_stickers (user_id, sticker_id, quantity) VALUES (?, ?, 1)",
                (user_id, sid),
            )
    db.commit()


def record_pack_opening(user_id, sticker_ids, db):
    db.execute(
        "INSERT INTO pack_openings (user_id, stickers_json) VALUES (?, ?)",
        (user_id, json.dumps(sticker_ids)),
    )
    db.commit()
