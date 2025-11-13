from flask import Blueprint, request, jsonify, redirect, session
from urllib.parse import urlencode
import requests
from models.models import RegisteredApp, OAuthSession, db
from utils.hash import create_bridge_token, create_jwt_token, verify_jwt_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
from routes.setting import get_setting_value


g_oauth = Blueprint("google_oauth", __name__, url_prefix="/google_oauth")

limiter = Limiter(key_func=get_remote_address)

# -------------------------------------------------------------
# STEP 1 — Redirect to Google
# -------------------------------------------------------------
@g_oauth.route("/login")
@limiter.limit("5 per minute")
def auth_login():
    client_id = request.args.get("client_id")
    redirect_url = request.args.get("redirect_url")
    if not client_id or not redirect_url:
        return jsonify({"error": "client_id and redirect_url required"}), 400

    reg = RegisteredApp.query.filter_by(client_id=client_id, is_active=True).first()    
    if not reg or redirect_url != reg.redirect_url:
        return jsonify({"error": "unauthorized client"}), 403

    session["bridge_client_id"] = client_id

    print('adasdas')
    GOOGLE_CLIENT_ID = get_setting_value("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = get_setting_value("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = get_setting_value("GOOGLE_REDIRECT_URI")

    if not GOOGLE_CLIENT_ID or not GOOGLE_REDIRECT_URI:
        return jsonify({"error": "Google OAuth settings not configured"}), 500

    params = {
        "client_id": GOOGLE_CLIENT_ID,        
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
        "state": client_id
    }
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}")

# -------------------------------------------------------------
# STEP 2 — Handle Google Callback
# -------------------------------------------------------------
@g_oauth.route("/callback")
def auth_callback():
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests

    code = request.args.get("code")
    if not code:
        return jsonify({"error": "missing code"}), 400

    client_id = session.get("bridge_client_id")
    if not client_id:
        return jsonify({"error": "missing session client"}), 400

    reg = RegisteredApp.query.filter_by(client_id=client_id, is_active=True).first()
    if not reg:
        return jsonify({"error": "unauthorized client"}), 403

    
    GOOGLE_CLIENT_ID = get_setting_value("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = get_setting_value("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = get_setting_value("GOOGLE_REDIRECT_URI")
    
    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=10
    )
    token_data = token_res.json()
    id_token_str = token_data.get("id_token")
    if not id_token_str:
        return jsonify({"error": "failed to obtain id_token", "detail": token_data}), 400

    try:
        idinfo = id_token.verify_oauth2_token(id_token_str, google_requests.Request(), GOOGLE_CLIENT_ID)
    except Exception as e:
        return jsonify({"error": "invalid google id_token", "detail": str(e)}), 400

    user_info = {
        "email": idinfo.get("email"),
        "name": idinfo.get("name"),
        "google_id": idinfo.get("sub")
    }

    # Create token (bridge internal)
    if reg.token_type == "django":
        token = create_jwt_token(user_info)
    else:
        token, _ = create_bridge_token(reg.client_id, user_info)
    
    db.session.add(OAuthSession(
        client_id=reg.client_id,
        email=user_info["email"],
        name=user_info["name"],
        google_id=user_info["google_id"],
        token=token,
        created_at=datetime.utcnow()
    ))
    db.session.commit()

    return redirect(f"{reg.redirect_url}?token={token}")

# -------------------------------------------------------------
# STEP 3 — Verify Token (for Django / CI)
# -------------------------------------------------------------
@g_oauth.route("/verify", methods=["POST"])
def auth_verify():
    token = request.json.get("token")
    if not token:
        return jsonify({"success": False, "error": "missing token"}), 400

    session_obj = OAuthSession.query.filter_by(token=token).first()
    if not session_obj:
        return jsonify({"success": False, "error": "invalid token"}), 403

    return jsonify({
        "success": True,
        "user": {
            "email": session_obj.email,
            "name": session_obj.name,
            "google_id": session_obj.google_id
        }
    })
