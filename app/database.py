import sqlite3
import os
import click
from flask import g, current_app


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    schema_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "schema.sql"
    )
    with open(schema_path, encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()


def seed_stickers():
    db = get_db()
    stickers = [
        (1, "Mbappé",      "França",     "legendary"),
        (2, "Vinicius Jr", "Brasil",     "rare"),
        (3, "Haaland",     "Noruega",    "rare"),
        (4, "Bellingham",  "Inglaterra", "common"),
        (5, "Pedri",       "Espanha",    "common"),
        (6, "Salah",       "Egito",      "common"),
        (7, "De Bruyne",   "Bélgica",    "common"),
    ]
    db.executemany(
        "INSERT OR IGNORE INTO stickers (number, player_name, country, rarity)"
        " VALUES (?, ?, ?, ?)",
        stickers,
    )
    db.commit()


@click.command("init-db")
def init_db_command():
    init_db()
    seed_stickers()
    click.echo("Banco de dados inicializado com 7 figurinhas.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
