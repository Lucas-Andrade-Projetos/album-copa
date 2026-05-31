import os

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-troque-em-producao")
DATABASE = os.path.join(os.path.dirname(__file__), "instance", "album.db")
PACKS_PER_DAY = int(os.environ.get("PACKS_PER_DAY", 5))
STICKERS_PER_PACK = int(os.environ.get("STICKERS_PER_PACK", 5))
