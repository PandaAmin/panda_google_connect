## main
from flask import Flask, render_template, request, redirect, session, url_for, flash

## model
from models.models import db, RegisteredApp

## config
from config import SECRET_KEY, DEBUG


## utils
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from datetime import datetime
import uuid

## registered_app
from routes.module import module
from routes.setting import pgc_setting
from routes.google_oauth import g_oauth


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
app.register_blueprint(module)
app.register_blueprint(pgc_setting)
app.register_blueprint(g_oauth)

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

############ Init ############

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=9003, debug=DEBUG)
