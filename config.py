import os

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-troque-em-producao")
DATABASE = os.path.join(os.path.dirname(__file__), "instance", "album.db")
PACKS_PER_DAY = int(os.environ.get("PACKS_PER_DAY", 5))
STICKERS_PER_PACK = int(os.environ.get("STICKERS_PER_PACK", 5))

# Protege o cookie de sessão contra acesso por JavaScript e CSRF básico
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
