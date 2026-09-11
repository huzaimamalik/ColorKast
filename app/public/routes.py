from time import perf_counter

from flask import Blueprint, flash, make_response, redirect, render_template, request, url_for

from app.color_utils import format_timing, rgb_to_hex
from app.extensions import db
from app.forms import ChooserForm, ClosestForm, SearchForm, TranslateForm
from app.models import Paint, PaletteItem
from app.public.services import (
    cleanup_palette, closest_paints, collection_choices, palette_session_id,
    save_palette_item, search_paints, translate_paint,
)

public = Blueprint("public", __name__)


def timed_operation(operation, *args):
    start = perf_counter()
    result = operation(*args)
    return result, (perf_counter() - start) * 1000


def timed_response(template, elapsed=None, **context):
    response = make_response(render_template(template, elapsed=elapsed, **context))
    if elapsed is not None:
        response.headers["X-Processing-Time-ms"] = format_timing(elapsed)
    return response


@public.get("/")
def home():
    return render_template("home.html")


@public.route("/chooser", methods=["GET", "POST"])
def chooser():
    form = ChooserForm(data={"red": 12, "green": 140, "blue": 220})
    rgb = (12, 140, 220)
    if form.validate_on_submit():
        rgb = (form.red.data, form.green.data, form.blue.data)
        if request.form.get("action") == "add":
            save_palette_item(rgb)
            flash("Custom Color added to your palette.", "success")
            return redirect(url_for("public.palette"))
        flash("Color preview updated.", "success")
    return render_template("chooser.html", form=form, rgb=rgb, hex_value=rgb_to_hex(rgb))


@public.get("/search")
def search():
    form = SearchForm(request.args)
    form.collection_id.choices = collection_choices(include_all=True)
    results, elapsed = None, None
    if request.args and form.validate():
        results, elapsed = timed_operation(search_paints, form.mode.data, form.query.data, form.collection_id.data)
    return timed_response("search.html", elapsed, form=form, results=results)


@public.get("/translate")
def translate():
    form = TranslateForm(request.args)
    form.collection_id.choices = form.target_id.choices = collection_choices()
    source, targets, elapsed, searched = None, [], None, False
    if request.args and form.validate():
        (source, targets), elapsed = timed_operation(translate_paint, form.paint_number.data, form.collection_id.data, form.target_id.data)
        searched = True
    return timed_response("translate.html", elapsed, form=form, source=source, targets=targets, searched=searched)


@public.get("/closest")
def closest():
    form = ClosestForm(request.args)
    form.collection_id.choices = form.target_id.choices = collection_choices()
    source, results, elapsed, searched = None, [], None, False
    if request.args and form.validate():
        (source, results), elapsed = timed_operation(closest_paints, form.paint_number.data, form.collection_id.data, form.scheme.data, form.target_id.data, form.count.data)
        searched = True
    return timed_response("closest.html", elapsed, form=form, source=source, results=results, searched=searched)


@public.get("/palette")
def palette():
    cleanup_palette()
    items = db.session.scalars(db.select(PaletteItem).where(PaletteItem.session_id == palette_session_id()).order_by(PaletteItem.added_at.desc(), PaletteItem.id.desc())).all()
    return render_template("palette.html", items=items)


@public.post("/palette/add")
def palette_add():
    paint_id = request.form.get("paint_id", type=int)
    paint = db.get_or_404(Paint, paint_id)
    save_palette_item(paint.rgb, paint)
    flash(f"{paint.name} added to your palette.", "success")
    return redirect(url_for("public.palette"))


@public.post("/palette/remove/<int:item_id>")
def palette_remove(item_id):
    cleanup_palette()
    item = db.first_or_404(db.select(PaletteItem).where(PaletteItem.id == item_id, PaletteItem.session_id == palette_session_id()))
    db.session.delete(item)
    db.session.commit()
    flash("Color removed from your palette.", "success")
    return redirect(url_for("public.palette"))


@public.post("/palette/clear")
def palette_clear():
    cleanup_palette()
    db.session.execute(db.delete(PaletteItem).where(PaletteItem.session_id == palette_session_id()))
    db.session.commit()
    flash("Your palette has been cleared.", "success")
    return redirect(url_for("public.palette"))
