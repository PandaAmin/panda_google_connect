from flask import Flask, render_template, request, redirect, session, url_for, jsonify , flash
from models.models import db, RegisteredApp
from config import SECRET_KEY, DEBUG
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from datetime import datetime

import uuid
# Import Google OAuth blueprint
from module.google_oauth import google_oauth_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config.from_object("config")

# DB
db.init_app(app)

# Security & rate limits
limiter = Limiter(key_func=get_remote_address, default_limits=["10 per minute"])
limiter.init_app(app)
Talisman(app, content_security_policy=None)

# Register the Google OAuth blueprint
app.register_blueprint(google_oauth_bp, url_prefix="/auth")

############ Home + Admin Login ############

@app.route("/")
def home():
    if "admin_logged_in" not in session:
        return redirect(url_for("login"))
    modules = RegisteredApp.query.all()
    return render_template("home.html", modules=modules)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Replace with real admin auth later (e.g. hashed password)
        if username == "admin" and password == "1234":
            session["admin_logged_in"] = True
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("login"))

############ Module Management ############

@app.route("/modules")
def modules():
    if "admin_logged_in" not in session:
        return redirect(url_for("login"))
    modules = RegisteredApp.query.all()
    return render_template("modules.html", modules=modules)

@app.route("/modules/register", methods=["POST"])
def register_module():
    if "admin_logged_in" not in session:
        return redirect(url_for("login"))

    data = request.form
    app_name = data.get("app_name")
    client_id = data.get("client_id")
    client_secret = data.get("client_secret")
    redirect_url = data.get("redirect_url")
    token_type = data.get("token_type", "ci")

    if not all([app_name, client_id, client_secret, redirect_url]):
        flash(f"Missing required fields", "danger")
        return redirect(url_for("modules"))

    if RegisteredApp.query.filter_by(app_name=app_name).first():
        flash(f"Module name '{app_name}' already exists.", "danger")
        return redirect(url_for("modules"))
      
    reg = RegisteredApp(
        app_name=app_name,
        client_id=client_id,
        client_secret=client_secret,
        redirect_url=redirect_url,
        token_type=token_type,
        is_active=True
    )
    db.session.add(reg)
    db.session.commit()
    
    return redirect(url_for("modules"))

@app.route("/modules/<int:module_id>/update", methods=["POST"])
def update_module(module_id):
    if "admin_logged_in" not in session:
        return redirect(url_for("login"))

    mod = RegisteredApp.query.get_or_404(module_id)
    app_name = request.form.get("app_name")
    redirect_url = request.form.get("redirect_url")
    token_type = request.form.get("token_type")
    
    duplicate = RegisteredApp.query.filter(
        RegisteredApp.app_name == app_name,
        RegisteredApp.id != module_id
    ).first()

    if duplicate:
        flash(f"Module name '{app_name}' already exists.", "danger")
        return redirect(url_for("modules"))

    # ✅ Update and save
    mod.app_name = app_name
    mod.redirect_url = redirect_url
    mod.token_type = token_type
    mod.updated_at = datetime.utcnow()
    db.session.commit()

    flash(f"Module '{app_name}' updated successfully!", "success")
    return redirect(url_for("modules"))


@app.route("/modules/<int:module_id>/delete", methods=["POST"])
def delete_module(module_id):
    if "admin_logged_in" not in session:
        return redirect(url_for("login"))

    mod = RegisteredApp.query.get_or_404(module_id)
    db.session.delete(mod)
    db.session.commit()
    
    flash("Module successfully deleted.", "success")
    
    return redirect(url_for("modules"))

@app.route("/modules/<int:module_id>/toggle")
def toggle_module(module_id):
    if "admin_logged_in" not in session:
        return redirect(url_for("login"))
    mod = RegisteredApp.query.get_or_404(module_id)
    mod.is_active = not mod.is_active
    db.session.commit()
    return redirect(url_for("modules"))

############ Init ############

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=9003, debug=DEBUG)
