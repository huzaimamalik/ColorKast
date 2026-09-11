from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from app.auth.permissions import can, require_capability
from app.extensions import db
from app.forms import AdminUserForm, PaintForm
from app.models import AdminUser, Collection, Paint, Translation
from app.public.services import collection_choices

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.get("")
@require_capability("view_admin")
def index():
    return render_template("admin/index.html")


@admin.get("/paints")
@require_capability("view_admin")
def paints():
    records = db.session.scalars(db.select(Paint).order_by(Paint.collection_id, Paint.paint_number, Paint.scheme)).all()
    return render_template("admin/paints.html", paints=records)


def paint_form(paint=None):
    form = PaintForm(obj=paint, data={"company": paint.collection.company} if paint else None)
    form.collection_id.choices = collection_choices()
    companies = db.session.scalars(db.select(Collection.company).distinct().order_by(Collection.company)).all()
    form.company.choices = [(company, company) for company in companies]
    return form


def translation_reference(paint_id):
    return db.session.scalar(db.select(Translation.id).where(
        (Translation.old_paint_id == paint_id) | (Translation.new_paint_id == paint_id),
    ).limit(1)) is not None


def save_paint(form, paint):
    collection = db.session.get(Collection, form.collection_id.data)
    if collection.company != form.company.data:
        form.company.errors.append("Company must match the selected collection.")
        return False
    if paint.id and translation_reference(paint.id):
        if paint.scheme != form.scheme.data or paint.collection_id != form.collection_id.data:
            form.scheme.errors.append("This paint has translations. Its scheme and collection cannot be changed.")
            return False
    for field in ("name", "paint_number", "scheme", "collection_id", "red", "green", "blue"):
        setattr(paint, field, getattr(form, field).data)
    db.session.add(paint)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        form.paint_number.errors.append("A paint with this number, collection, and scheme already exists.")
        return False
    return True


@admin.route("/paints/new", methods=["GET", "POST"])
@require_capability("add_paint")
def paint_new():
    form = paint_form()
    if form.validate_on_submit() and save_paint(form, Paint()):
        flash("Paint added successfully.", "success")
        return redirect(url_for("admin.paints"))
    return render_template("admin/paint_form.html", form=form, title="Add paint")


@admin.route("/paints/<int:paint_id>/edit", methods=["GET", "POST"])
@require_capability("update_paint")
def paint_edit(paint_id):
    paint = db.get_or_404(Paint, paint_id)
    form = paint_form(paint)
    if form.validate_on_submit() and save_paint(form, paint):
        flash("Paint updated successfully.", "success")
        return redirect(url_for("admin.paints"))
    return render_template("admin/paint_form.html", form=form, title="Update paint")


@admin.post("/paints/<int:paint_id>/delete")
@require_capability("delete_paint")
def paint_delete(paint_id):
    paint = db.get_or_404(Paint, paint_id)
    if translation_reference(paint_id):
        flash("Cannot delete this paint because it is referenced by a translation.", "warning")
    else:
        db.session.delete(paint)
        db.session.commit()
        flash("Paint deleted. Existing palette snapshots are preserved.", "success")
    return redirect(url_for("admin.paints"))


@admin.get("/users")
@require_capability("view_admin")
def users():
    records = db.session.scalars(db.select(AdminUser).order_by(AdminUser.level, AdminUser.username)).all()
    return render_template("admin/users.html", users=records)


@admin.route("/users/new", methods=["GET", "POST"])
@require_capability("view_admin")
def user_new():
    form = AdminUserForm()
    form.level.choices = [(level, f"Level {level}") for level in (1, 2, 3) if can(f"create_admin_level_{level}")]
    if request.method == "POST":
        requested_level = request.form.get("level", type=int)
        if requested_level in (1, 2, 3) and not can(f"create_admin_level_{requested_level}"):
            abort(403)
    if form.validate_on_submit():
        user = AdminUser(username=form.username.data, level=form.level.data, created_by=current_user.id)
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            form.username.errors.append("This username is already in use.")
        else:
            flash("Administrator created successfully.", "success")
            return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form)
