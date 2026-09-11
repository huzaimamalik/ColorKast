import re
import secrets

import pytest

from app import create_app
from app.extensions import db
from seed import seed_database


@pytest.fixture
def app(tmp_path, monkeypatch):
    passwords = {level: secrets.token_urlsafe(20) for level in (1, 2, 3)}
    for level, password in passwords.items():
        monkeypatch.setenv(f"ADMIN_L{level}_PASSWORD", password)
    application = create_app({
        "TESTING": True,
        "SECRET_KEY": secrets.token_hex(32),
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + (tmp_path / "test.db").as_posix(),
        "SESSION_COOKIE_SECURE": False,
    })
    application.config["DEMO_TEST_PASSWORDS"] = passwords
    with application.app_context():
        seed_database()
    yield application
    with application.app_context():
        db.session.remove()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


def csrf_token(client, page="/chooser"):
    response = client.get(page)
    assert response.status_code == 200
    match = re.search(rb'name="csrf_token"[^>]*value="([^"]+)"', response.data)
    assert match, f"No CSRF token on {page}"
    return match.group(1).decode()


def post_form(client, path, data=None, page="/chooser", follow_redirects=True):
    payload = dict(data or {})
    payload["csrf_token"] = csrf_token(client, page)
    return client.post(path, data=payload, follow_redirects=follow_redirects)


def login(client, app, level):
    response = post_form(client, "/admin/login", {
        "username": f"level{level}admin",
        "password": app.config["DEMO_TEST_PASSWORDS"][level],
    }, page="/admin/login")
    assert b"Signed in successfully" in response.data
    return response
