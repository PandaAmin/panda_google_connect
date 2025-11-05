import os
from datetime import timedelta
from urllib.parse import quote_plus


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# GENERAL
ENV = os.getenv("FLASK_ENV", "development")
DEBUG = ENV != "production"
SECRET_KEY = "D6B6859AA41911F0B88C000D3AA21DB9"

# DB 

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "adnap")
DB_HOST = os.getenv("DB_HOST", "192.168.15.230")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "panda_google_auth")

SQLALCHEMY_DATABASE_URI = f"mysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_recycle': 300,
    'pool_pre_ping': True
}

# SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'bridge.db')}")
# SQLALCHEMY_TRACK_MODIFICATIONS = False

# Google OAuth config
# GOOGLE_CLIENT_ID = "427454940518-90lb882gbli6epvfkq1ndefbu186c68r.apps.googleusercontent.com"
# GOOGLE_CLIENT_SECRET = "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"
# GOOGLE_REDIRECT_URI = "http://localhost:9003/auth/callback"


# Tokens
BRIDGE_TOKEN_EXPIRE_SECONDS = int(os.getenv("BRIDGE_TOKEN_EXPIRE_SECONDS", 3600))  # for CI tokens
JWT_SECRET = os.getenv("JWT_SECRET", "replace-with-jwt-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))