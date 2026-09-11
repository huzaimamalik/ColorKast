"""SRS Sections 4.2, 4.5, and 4.6: persisted paints, mappings, admins, and snapshots."""
from datetime import datetime, timezone
import sqlite3

from flask_login import UserMixin
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


def utcnow():
    # SQLite stores naive datetimes; all persisted timestamps are UTC.
    return datetime.now(timezone.utc).replace(tzinfo=None)


@event.listens_for(Engine, "connect")
def enable_foreign_keys(connection, _record):
    if isinstance(connection, sqlite3.Connection):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class ColorValues:
    @property
    def rgb(self):
        return self.red, self.green, self.blue

    @property
    def hex_value(self):
        return "#{:02X}{:02X}{:02X}".format(*self.rgb)


class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    __table_args__ = (db.UniqueConstraint("name", "company"),)


class Paint(ColorValues, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    paint_number = db.Column(db.String(40), nullable=False, index=True)
    scheme = db.Column(db.String(3), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey("collection.id"), nullable=False, index=True)
    collection = db.relationship("Collection", lazy="joined")
    red = db.Column(db.Integer, nullable=False)
    green = db.Column(db.Integer, nullable=False)
    blue = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)
    __table_args__ = (
        db.UniqueConstraint("paint_number", "collection_id", "scheme"),
        db.CheckConstraint("scheme IN ('old', 'new')"),
        db.CheckConstraint("red BETWEEN 0 AND 255 AND green BETWEEN 0 AND 255 AND blue BETWEEN 0 AND 255"),
    )


class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    old_paint_id = db.Column(db.Integer, db.ForeignKey("paint.id", ondelete="RESTRICT"), nullable=False)
    new_paint_id = db.Column(db.Integer, db.ForeignKey("paint.id", ondelete="RESTRICT"), nullable=False)
    old_paint = db.relationship("Paint", foreign_keys=[old_paint_id], lazy="joined")
    new_paint = db.relationship("Paint", foreign_keys=[new_paint_id], lazy="joined")
    __table_args__ = (db.UniqueConstraint("old_paint_id", "new_paint_id"),)


@event.listens_for(Session, "before_flush")
def validate_translation_schemes(session, _flush_context, _instances):
    for record in session.new.union(session.dirty):
        if isinstance(record, Translation):
            old = record.old_paint or session.get(Paint, record.old_paint_id)
            new = record.new_paint or session.get(Paint, record.new_paint_id)
            if old is None or new is None or old.scheme != "old" or new.scheme != "new":
                raise ValueError("Translations must map an old-scheme paint to a new-scheme paint.")


class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("admin_user.id"))
    __table_args__ = (db.CheckConstraint("level IN (1, 2, 3)"),)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="scrypt")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class PaletteItem(ColorValues, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), nullable=False, index=True)
    paint_id = db.Column(db.Integer, db.ForeignKey("paint.id", ondelete="SET NULL"))
    label = db.Column(db.String(100), nullable=False)
    paint_number = db.Column(db.String(40))
    collection_name = db.Column(db.String(100))
    red = db.Column(db.Integer, nullable=False)
    green = db.Column(db.Integer, nullable=False)
    blue = db.Column(db.Integer, nullable=False)
    added_at = db.Column(db.DateTime, nullable=False, default=utcnow, index=True)
    __table_args__ = (
        db.CheckConstraint("red BETWEEN 0 AND 255 AND green BETWEEN 0 AND 255 AND blue BETWEEN 0 AND 255"),
    )
