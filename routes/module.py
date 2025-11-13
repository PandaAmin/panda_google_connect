from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from models.models import db, RegisteredApp
from datetime import datetime

module = Blueprint("module", __name__, url_prefix="/modules")

@module.route("/")
def modules():
    if "admin_logged_in" not in session:
        return redirect(url_for("login"))
    modules = RegisteredApp.query.all()
    return render_template("modules.html", modules=modules)


@module.route("/register", methods=["POST"])
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
        flash("Missing required fields", "danger")
        return redirect(url_for("module.modules"))

    if RegisteredApp.query.filter_by(app_name=app_name).first():
        flash(f"Module name '{app_name}' already exists.", "danger")
        return redirect(url_for("module.modules"))

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

    flash(f"Module '{app_name}' registered successfully!", "success")
    return redirect(url_for("module.modules"))


@module.route("/<int:module_id>/update", methods=["POST"])
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
        return redirect(url_for("module.modules"))

    mod.app_name = app_name
    mod.redirect_url = redirect_url
    mod.token_type = token_type
    mod.updated_at = datetime.utcnow()
    db.session.commit()

    flash(f"Module '{app_name}' updated successfully!", "success")
    return redirect(url_for("module.modules"))


@module.route("/<int:module_id>/delete", methods=["POST"])
def delete_module(module_id):
    if "admin_logged_in" not in session:
        return redirect(url_for("login"))

    mod = RegisteredApp.query.get_or_404(module_id)
    db.session.delete(mod)
    db.session.commit()

    flash("Module successfully deleted.", "success")
    return redirect(url_for("module.modules"))


@module.route("/<int:module_id>/toggle")
def toggle_module(module_id):
    if "admin_logged_in" not in session:
        return redirect(url_for("login"))

    mod = RegisteredApp.query.get_or_404(module_id)
    mod.is_active = not mod.is_active
    db.session.commit()

    flash(f"Module '{mod.app_name}' status has been changed.", "success")
    return redirect(url_for("module.modules"))
