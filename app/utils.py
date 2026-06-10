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


def draw_stickers(db, n):
    todas = db.execute(
        "SELECT id, player_name, country, rarity FROM stickers"
    ).fetchall()

    population = list(todas)
    weights    = [RARITY_WEIGHTS.get(s["rarity"], 10) for s in population]

    sorteadas = random.choices(population, weights=weights, k=n)
    return sorteadas


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
