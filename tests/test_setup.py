import pytest
from sqlalchemy.exc import OperationalError

from app import create_app
from app.extensions import db
from app.models import AdminUser, Paint, Translation
from seed import seed_database


def test_seed_is_repeatable_and_requires_passwords(app, monkeypatch):
    with app.app_context():
        original_hash = db.session.get(AdminUser, 1).password_hash
        seed_database()
        assert db.session.scalar(db.select(db.func.count(Paint.id))) == 40
        assert db.session.scalar(db.select(db.func.count(Translation.id))) == 20
        assert db.session.get(AdminUser, 1).password_hash == original_hash
        monkeypatch.delenv("ADMIN_L2_PASSWORD")
        with pytest.raises(ValueError, match="ADMIN_L2_PASSWORD"):
            seed_database()
    result = app.test_cli_runner().invoke(args=["init-db"])
    assert result.exit_code == 0
    result = app.test_cli_runner().invoke(args=["seed"])
    assert result.exit_code != 0 and "ADMIN_L2_PASSWORD" in result.output


def test_secret_key_required():
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app({"SECRET_KEY": ""})


def test_friendly_database_error(app, client, monkeypatch, caplog):
    def fail(*args, **kwargs):
        raise OperationalError("private database details", {}, RuntimeError("internal problem"))
    monkeypatch.setattr(db.session, "scalars", fail)
    response = client.get("/search")
    assert response.status_code == 500
    assert b"Something went wrong" in response.data
    assert b"private database details" not in response.data
    assert "Database operation failed" in caplog.text
