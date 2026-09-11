"""Fictional deterministic data; reruns preserve existing records and passwords."""
import os

from app.extensions import db
from app.models import AdminUser, Collection, Paint, Translation

COLLECTIONS = [
    ("Heritage", "ABC Paint", "old", "H"),
    ("Horizon", "ABC Paint", "new", "N"),
    ("Studio", "ABC Paint", "new", "S"),
    ("Meadow", "Fictional Field Paint", "old", "M"),
]
COLORS = [
    ("Harbor Blue", (32, 102, 158)),
    ("Desert Sand", (214, 188, 145)),
    ("Pine Grove", (42, 100, 65)),
    ("Sunset Clay", (195, 99, 74)),
    ("Silver Mist", (178, 190, 196)),
    ("Deep Plum", (90, 48, 99)),
    ("Golden Field", (234, 183, 54)),
    ("Rose Petal", (222, 153, 163)),
    ("Chalk White", (255, 255, 255)),
    ("Midnight Ink", (0, 0, 0)),
]


def seed_database():
    passwords = {level: os.environ.get(f"ADMIN_L{level}_PASSWORD", "") for level in (1, 2, 3)}
    invalid = [f"ADMIN_L{level}_PASSWORD" for level, value in passwords.items() if not 12 <= len(value) <= 128]
    if invalid:
        raise ValueError("Supply passwords of 12–128 characters through environment variables: " + ", ".join(invalid))
    db.create_all()
    catalog = {}
    for offset, (name, company, scheme, prefix) in enumerate(COLLECTIONS):
        collection = db.session.scalar(db.select(Collection).where(Collection.name == name, Collection.company == company))
        if collection is None:
            collection = Collection(name=name, company=company)
            db.session.add(collection)
            db.session.flush()
        for index, (color_name, base_rgb) in enumerate(COLORS, start=1):
            # The shared number 100 demonstrates exact matches across collections.
            number = "100" if index == 10 else f"{prefix}{index:03d}"
            paint = db.session.scalar(db.select(Paint).where(Paint.paint_number == number, Paint.collection_id == collection.id, Paint.scheme == scheme))
            if paint is None:
                rgb = tuple(max(0, min(255, component + offset * (4 if channel != 1 else -3))) for channel, component in enumerate(base_rgb))
                paint = Paint(name=color_name, paint_number=number, scheme=scheme, collection=collection, red=rgb[0], green=rgb[1], blue=rgb[2])
                db.session.add(paint)
                db.session.flush()
            catalog[(prefix, index)] = paint
    for source_prefix, target_prefix, count in [("H", "N", 8), ("H", "S", 5), ("M", "N", 7)]:
        for index in range(1, count + 1):
            old, new = catalog[(source_prefix, index)], catalog[(target_prefix, index)]
            existing = db.session.scalar(db.select(Translation).where(Translation.old_paint_id == old.id, Translation.new_paint_id == new.id))
            if existing is None:
                db.session.add(Translation(old_paint=old, new_paint=new))
    for level, password in passwords.items():
        username = f"level{level}admin"
        if db.session.scalar(db.select(AdminUser).where(AdminUser.username == username)) is None:
            user = AdminUser(username=username, level=level)
            user.set_password(password)
            db.session.add(user)
    db.session.commit()


if __name__ == "__main__":
    from app import create_app
    with create_app().app_context():
        try:
            seed_database()
        except ValueError as error:
            raise SystemExit(str(error)) from error
        print("Demo seed complete. Existing records and passwords preserved.")
