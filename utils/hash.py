import secrets, time
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES, BRIDGE_TOKEN_EXPIRE_SECONDS
from models.models import db, RegisteredApp, BridgeToken

######### Client secret helpers #########
def hash_secret(secret: str) -> str:
    # PBKDF2 hashing via werkzeug
    return generate_password_hash(secret)

def verify_secret(hash_value: str, plain_secret: str) -> bool:
    return check_password_hash(hash_value, plain_secret)

######### Token helpers #########
def create_bridge_token(client_id: str, user_info: dict):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(seconds=BRIDGE_TOKEN_EXPIRE_SECONDS)
    bt = BridgeToken(
        token=token,
        client_id=client_id,
        user_email=user_info["email"],
        user_name=user_info.get("name"),
        expires_at=expires_at
    )
    db.session.add(bt)
    db.session.commit()
    return token, expires_at

def verify_bridge_token(token: str):
    bt = BridgeToken.query.filter_by(token=token).first()
    if not bt:
        return None
    if bt.is_expired():
        # revoke expired
        db.session.delete(bt)
        db.session.commit()
        return None
    return {"email": bt.user_email, "name": bt.user_name, "client_id": bt.client_id}

######### JWT helpers for Django usage #########
def create_jwt_token(user_info: dict):
    payload = {
        "email": user_info["email"],
        "name": user_info.get("name"),
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    # In PyJWT >=2, jwt.encode returns str by default when algorithm provided
    return token

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "expired"}
    except Exception as e:
        return {"error": "invalid"}
