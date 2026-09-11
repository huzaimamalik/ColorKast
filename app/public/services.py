"""Database-backed lookups; templates and network time are outside these operations."""
from datetime import timedelta
from uuid import uuid4

from flask import session

from app.color_utils import hex_to_rgb, rank_closest, validate_rgb
from app.extensions import db
from app.models import Collection, Paint, PaletteItem, Translation, utcnow


def collection_choices(include_all=False):
    collections = db.session.scalars(db.select(Collection).order_by(Collection.id)).all()
    choices = [(item.id, f"{item.name} — {item.company}") for item in collections]
    return ([(0, "All collections")] + choices) if include_all else choices


def search_paints(mode, value, collection_id):
    statement = db.select(Paint)
    if collection_id:
        statement = statement.where(Paint.collection_id == collection_id)
    if mode == "name":
        # Literal substring search: escape SQL LIKE wildcard characters.
        escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        statement = statement.where(Paint.name.ilike(f"%{escaped}%", escape="\\"))
    elif mode == "number":
        statement = statement.where(Paint.paint_number == value)
    elif mode in {"rgb", "hex"}:
        rgb = hex_to_rgb(value) if mode == "hex" else validate_rgb(*value.split(","))
        statement = statement.where(Paint.red == rgb[0], Paint.green == rgb[1], Paint.blue == rgb[2])
    else:
        raise ValueError("Choose a supported search mode.")
    return db.session.scalars(statement.order_by(Paint.name, Paint.id)).all()


def find_source(paint_number, collection_id, scheme):
    return db.session.scalar(db.select(Paint).where(
        Paint.paint_number == paint_number, Paint.collection_id == collection_id, Paint.scheme == scheme,
    ))


def translate_paint(paint_number, collection_id, target_id):
    source = find_source(paint_number, collection_id, "old")
    if source is None:
        return None, []
    targets = db.session.scalars(db.select(Paint).join(Translation, Translation.new_paint_id == Paint.id).where(
        Translation.old_paint_id == source.id, Paint.collection_id == target_id,
    ).order_by(Paint.id)).all()
    return source, targets


def closest_paints(paint_number, collection_id, scheme, target_id, count):
    source = find_source(paint_number, collection_id, scheme)
    if source is None:
        return None, []
    candidates = db.session.scalars(db.select(Paint).where(Paint.collection_id == target_id)).all()
    return source, rank_closest(source.rgb, candidates, count)


def palette_session_id():
    if "palette_session_id" not in session:
        session["palette_session_id"] = str(uuid4())
    session.permanent = True
    return session["palette_session_id"]


def cleanup_palette():
    """SRS Section 4.5: expire individual snapshots at 30 days, even in active sessions."""
    cutoff = utcnow() - timedelta(days=30)
    db.session.execute(db.delete(PaletteItem).where(PaletteItem.added_at <= cutoff))
    db.session.commit()


def save_palette_item(rgb, paint=None):
    cleanup_palette()
    rgb = validate_rgb(*rgb)
    item = PaletteItem(
        session_id=palette_session_id(), red=rgb[0], green=rgb[1], blue=rgb[2],
        paint_id=paint.id if paint else None,
        label=paint.name if paint else "Custom Color",
        paint_number=paint.paint_number if paint else None,
        collection_name=paint.collection.name if paint else None,
    )
    db.session.add(item)
    db.session.commit()
    return item
