from flask import Blueprint, flash, redirect, render_template, session, url_for
from flask_login import current_user, login_user, logout_user

from app.extensions import db
from app.forms import LoginForm
from app.models import AdminUser

auth = Blueprint("auth", __name__, url_prefix="/admin")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(AdminUser).where(AdminUser.username == form.username.data))
        if user and user.check_password(form.password.data):
            palette_id = session.get("palette_session_id")
            session.clear()
            if palette_id:
                session["palette_session_id"] = palette_id
            session.permanent = True
            login_user(user)
            flash("Signed in successfully.", "success")
            return redirect(url_for("admin.index"))
        flash("Invalid username or password.", "error")
    return render_template("admin/login.html", form=form)


@auth.post("/logout")
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("public.home"))
