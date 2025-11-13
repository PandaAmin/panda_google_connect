from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from models.models import db, AppSetting
from datetime import datetime

pgc_setting = Blueprint("setting", __name__, url_prefix="/settings")

@pgc_setting.route("/")
def settings():
    if "admin_logged_in" not in session:
        return redirect(url_for("login"))
    settings_data = AppSetting.query.order_by(AppSetting.key.asc()).all()
    
    return render_template("setting.html", settings=settings_data)

@pgc_setting.route("/add", methods=["GET", "POST"])
def add_setting():
    if "admin_logged_in" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        key = request.form.get("key")
        value = request.form.get("value")
        description = request.form.get("description")

        # Check duplicate key
        existing = AppSetting.query.filter_by(key=key).first()
        if existing:
            flash("Setting with that key already exists.", "danger")
        else:
            new_setting = AppSetting(
                key=key,
                value=value,
                description=description,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(new_setting)
            db.session.commit()
            flash("New setting added successfully!", "success")
            return redirect(url_for("setting.settings"))

    return render_template("setting_form.html", action="Add", setting=None)

@pgc_setting.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_setting(id):
    if "admin_logged_in" not in session:
        return redirect(url_for("login"))

    setting = AppSetting.query.get_or_404(id)

    if request.method == "POST":
        setting.key = request.form.get("key")
        setting.value = request.form.get("value")
        setting.description = request.form.get("description")
        setting.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Setting updated successfully!", "success")
        return redirect(url_for("setting.settings"))

    return render_template("setting_form.html", action="Edit", setting=setting)

@pgc_setting.route("/delete/<int:id>", methods=["POST"])
def delete_setting(id):
    if "admin_logged_in" not in session:
        return redirect(url_for("login"))

    setting = AppSetting.query.get_or_404(id)
    db.session.delete(setting)
    db.session.commit()
    flash("Setting deleted successfully!", "success")
    return redirect(url_for("setting.settings"))



def get_setting_value(key):
    setting = AppSetting.query.filter_by(key=key).first()
    return setting.value if setting else None