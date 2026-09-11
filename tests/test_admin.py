import secrets

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import AdminUser, Paint, PaletteItem, Translation
from conftest import login, post_form


def paint_data(**changes):
    data = {"name": "Test paint", "paint_number": "TEST-001", "scheme": "new", "collection_id": 2, "company": "ABC Paint", "red": 0, "green": 128, "blue": 255}
    return data | changes


@pytest.mark.parametrize("path", ["/admin", "/admin/paints", "/admin/paints/new", "/admin/paints/1/edit", "/admin/users", "/admin/users/new"])
def test_anonymous_admin_access_denied(client, path):
    assert client.get(path).status_code == 403


@pytest.mark.parametrize("level", [1, 2, 3])
def test_paint_capabilities(app, client, level):
    login(client, app, level)
    assert b"Paint added successfully" in post_form(client, "/admin/paints/new", paint_data()).data
    with app.app_context():
        paint_id = db.session.scalar(db.select(Paint.id).where(Paint.paint_number == "TEST-001"))
    edited = post_form(client, f"/admin/paints/{paint_id}/edit", paint_data(name="Updated"))
    assert (edited.status_code == 403) == (level == 1)
    assert client.get(f"/admin/paints/{paint_id}/edit").status_code == (403 if level == 1 else 200)
    with app.app_context():
        assert db.session.get(Paint, paint_id).name == ("Test paint" if level == 1 else "Updated")
    deleted = post_form(client, f"/admin/paints/{paint_id}/delete")
    assert (deleted.status_code == 403) == (level < 3)
    with app.app_context():
        assert (db.session.get(Paint, paint_id) is None) == (level == 3)


@pytest.mark.parametrize("actor,target", [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)])
def test_admin_creation_matrix(app, client, actor, target):
    login(client, app, actor)
    password = secrets.token_urlsafe(20)
    response = post_form(client, "/admin/users/new", {"username": "newadmin", "password": password, "level": target})
    assert response.status_code == (403 if target > actor else 200)
    with app.app_context():
        user = db.session.scalar(db.select(AdminUser).where(AdminUser.username == "newadmin"))
        if target > actor:
            assert user is None
        else:
            assert user.level == target and user.password_hash != password and user.check_password(password)


def test_invalid_admin_level_and_duplicate_user(app, client):
    login(client, app, 3)
    for level in (0, 4, "abc"):
        response = post_form(client, "/admin/users/new", {"username": "newadmin", "password": secrets.token_urlsafe(20), "level": level})
        assert b"Please correct the form" in response.data
    response = post_form(client, "/admin/users/new", {"username": "level1admin", "password": secrets.token_urlsafe(20), "level": 1})
    assert b"already in use" in response.data


@pytest.mark.parametrize("changes", [{"name": "   "}, {"paint_number": ""}, {"scheme": "other"}, {"collection_id": 999}, {"company": "Fictional Field Paint"}, {"red": -1}, {"blue": 256}, {"green": "2.5"}])
def test_paint_validation(app, client, changes):
    login(client, app, 3)
    response = post_form(client, "/admin/paints/new", paint_data(**changes))
    assert b"Please correct the form" in response.data
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(Paint.id))) == 40


def test_duplicate_and_translation_integrity(app, client):
    login(client, app, 3)
    response = post_form(client, "/admin/paints/new", paint_data(paint_number="N001"))
    assert b"already exists" in response.data
    response = post_form(client, "/admin/paints/1/delete")
    assert b"referenced by a translation" in response.data
    response = post_form(client, "/admin/paints/1/edit", paint_data(paint_number="H001", scheme="new", collection_id=1))
    assert b"scheme and collection cannot be changed" in response.data
    with app.app_context():
        assert db.session.get(Paint, 1).scheme == "old"
        invalid = Translation(old_paint=db.session.get(Paint, 11), new_paint=db.session.get(Paint, 1))
        db.session.add(invalid)
        with pytest.raises(ValueError):
            db.session.commit()
        db.session.rollback()
        db.session.delete(db.session.get(Paint, 1))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_paint_delete_keeps_palette_snapshot(app, client):
    post_form(client, "/palette/add", {"paint_id": 9})
    login(client, app, 3)
    assert b"Paint deleted" in post_form(client, "/admin/paints/9/delete").data
    response = client.get("/palette")
    assert b"Chalk White" in response.data and b"#FFFFFF" in response.data
    with app.app_context():
        assert db.session.scalar(db.select(PaletteItem)).paint_id is None


def test_login_logout_and_generic_failure(app, client):
    for username in ("level1admin", "nonexistent"):
        response = post_form(client, "/admin/login", {"username": username, "password": secrets.token_urlsafe(20)}, page="/admin/login")
        assert b"Invalid username or password" in response.data
    login(client, app, 1)
    assert client.post("/admin/paints/new", data=paint_data()).status_code == 400
    assert b"signed out" in post_form(client, "/admin/logout").data
    assert client.get("/admin").status_code == 403
