CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL UNIQUE,
    password    TEXT    NOT NULL,
    is_admin    INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS stickers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    number      INTEGER NOT NULL UNIQUE,
    player_name TEXT    NOT NULL,
    country     TEXT    NOT NULL,
    rarity      TEXT    NOT NULL DEFAULT 'common'
);

CREATE TABLE IF NOT EXISTS user_stickers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    sticker_id  INTEGER NOT NULL REFERENCES stickers(id),
    quantity    INTEGER NOT NULL DEFAULT 1,
    obtained_at TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, sticker_id)
);

CREATE TABLE IF NOT EXISTS pack_openings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(id),
    opened_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    stickers_json TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS admin_overrides (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    target_user_id INTEGER REFERENCES users(id),
    sticker_id     INTEGER NOT NULL REFERENCES stickers(id),
    used           INTEGER NOT NULL DEFAULT 0,
    created_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);
