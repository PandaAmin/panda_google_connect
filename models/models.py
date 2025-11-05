from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class RegisteredApp(db.Model):
    __tablename__ = "registered_apps"
    id = db.Column(db.Integer, primary_key=True)
    app_name = db.Column(db.String(120), nullable=False)
    client_id = db.Column(db.String(120), unique=True, nullable=False)  # public ID
    client_secret = db.Column(db.String(256), nullable=False)   
    redirect_url = db.Column(db.String(500), nullable=False)
    token_type = db.Column(db.String(20), nullable=False)  # 'django' or 'ci'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BridgeToken(db.Model):
    __tablename__ = "bridge_tokens"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(128), unique=True, nullable=False)
    client_id = db.Column(db.String(120), db.ForeignKey("registered_apps.client_id"), nullable=False)
    user_email = db.Column(db.String(240), nullable=False)
    user_name = db.Column(db.String(240), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

class OAuthSession(db.Model):
    __tablename__ = "oauth_sessions"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    google_id = db.Column(db.String(120), nullable=True)
    token = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class AppSetting(db.Model):
    __tablename__ = 'app_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AppSetting {self.key}>'