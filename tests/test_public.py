from datetime import timedelta

import pytest

from app.extensions import db
from app.models import Collection, Paint, PaletteItem, utcnow
from app.public.services import closest_paints
from conftest import post_form


@pytest.mark.parametrize("path", ["/", "/chooser", "/search", "/translate", "/closest", "/palette", "/admin/login"])
def test_public_pages_load(client, path):
    assert client.get(path).status_code == 200


@pytest.mark.parametrize("mode,query,expected", [
    ("name", "hArBoR", 4), ("number", "100", 4),
    ("rgb", "32,102,158", 1), ("hex", "#20669E", 1), ("hex", "20669e", 1),
])
def test_search_modes(client, mode, query, expected):
    response = client.get("/search", query_string={"mode": mode, "query": query, "collection_id": 0})
    assert response.status_code == 200
    assert response.data.count(b'class="paint-card"') == expected
    assert float(response.headers["X-Processing-Time-ms"]) > 0
    assert b"Server processing time:" in response.data


def test_collection_filter_and_no_result(client):
    response = client.get("/search?mode=number&query=100&collection_id=2")
    assert response.data.count(b'class="paint-card"') == 1
    for query in ("not-a-real-paint", "%", "_", "' OR 1=1 --"):
        response = client.get("/search", query_string={"mode": "name", "query": query, "collection_id": 0})
        assert b"No matching paints found" in response.data


@pytest.mark.parametrize("mode,query", [("rgb", "256,0,0"), ("rgb", "1.5,0,0"), ("rgb", "0,0"), ("hex", "#FFF"), ("name", "   ")])
def test_invalid_search(client, mode, query):
    response = client.get("/search", query_string={"mode": mode, "query": query, "collection_id": 0})
    assert b"Please correct the form" in response.data
    assert "X-Processing-Time-ms" not in response.headers


def test_invalid_collection_rejected(client):
    assert b"Not a valid choice" in client.get("/search?mode=name&query=harbor&collection_id=999").data


def test_translator_success_missing_and_unknown(client):
    response = client.get("/translate?paint_number=H001&collection_id=1&target_id=2")
    assert b"H001" in response.data and b"N001" in response.data
    assert float(response.headers["X-Processing-Time-ms"]) > 0
    response = client.get("/translate?paint_number=H001&collection_id=1&target_id=3")
    assert b"S001" in response.data and b"N001" not in response.data
    assert b"No translation available" in client.get("/translate?paint_number=H006&collection_id=1&target_id=3").data
    assert b"Unknown source paint" in client.get("/translate?paint_number=UNKNOWN&collection_id=1&target_id=2").data


def test_closest_ranking_large_count_and_empty(app, client):
    with app.app_context():
        source, results = closest_paints("H001", 1, "old", 2, 100)
        assert source.paint_number == "H001"
        assert len(results) == 10 and results[0][0].paint_number == "N001"
        distances = [distance for _, distance in results]
        assert distances == sorted(distances)
        empty = Collection(name="Empty test collection", company="ABC Paint")
        db.session.add(empty)
        db.session.commit()
        empty_id = empty.id
    response = client.get("/closest?paint_number=H001&collection_id=1&scheme=old&target_id=2&count=100")
    assert response.data.count(b'class="paint-card"') == 10
    assert float(response.headers["X-Processing-Time-ms"]) > 0
    assert b"no paints available" in client.get(f"/closest?paint_number=H001&collection_id=1&scheme=old&target_id={empty_id}&count=5").data
    assert b"Unknown source paint" in client.get("/closest?paint_number=X&collection_id=1&scheme=old&target_id=2&count=5").data


@pytest.mark.parametrize("count", ["0", "-1", "1.5", "abc"])
def test_closest_invalid_count(client, count):
    response = client.get(f"/closest?paint_number=H001&collection_id=1&scheme=old&target_id=2&count={count}")
    assert b"Please correct the form" in response.data


@pytest.mark.parametrize("value,valid", [("0", True), ("255", True), ("-1", False), ("256", False), ("1.5", False)])
def test_chooser_validation(client, value, valid):
    response = post_form(client, "/chooser", {"red": value, "green": value, "blue": value, "action": "preview"})
    assert (b"Color preview updated" in response.data) == valid
    assert (b"Please correct the form" in response.data) != valid


def test_palette_isolation_snapshot_expiry_remove_clear(app, client):
    other = app.test_client()
    assert b"added to your palette" in post_form(client, "/palette/add", {"paint_id": 9}).data
    post_form(client, "/palette/add", {"paint_id": 9})
    post_form(other, "/palette/add", {"paint_id": 1})
    with app.app_context():
        items = db.session.scalars(db.select(PaletteItem).order_by(PaletteItem.id)).all()
        first_id, second_id, other_id = [item.id for item in items]
        assert items[0].session_id != items[2].session_id
        paint = db.session.get(Paint, 9)
        paint.red = 12
        paint.name = "Changed paint name"
        db.session.commit()
    assert post_form(other, f"/palette/remove/{first_id}").status_code == 404
    assert b"Chalk White" in client.get("/palette").data
    assert b"#FFFFFF" in client.get("/palette").data
    assert b"Harbor Blue" not in client.get("/palette").data
    assert b"Color removed" in post_form(client, f"/palette/remove/{second_id}").data
    with app.app_context():
        db.session.get(PaletteItem, first_id).added_at = utcnow() - timedelta(days=30, seconds=1)
        db.session.commit()
    assert b"No saved colors yet" in client.get("/palette").data
    post_form(client, "/chooser", {"red": 0, "green": 128, "blue": 255, "action": "add"})
    assert b"Custom Color" in client.get("/palette").data
    assert b"#0080FF" in client.get("/palette").data
    post_form(client, "/palette/clear")
    assert b"No saved colors yet" in client.get("/palette").data
    with app.app_context():
        assert db.session.get(PaletteItem, other_id) is not None


def test_palette_survives_browser_client_recreation(app, client):
    post_form(client, "/palette/add", {"paint_id": 1})
    cookie = client.get_cookie("session")
    assert cookie.http_only and cookie.same_site == "Lax" and cookie.expires is not None
    resumed = app.test_client()
    resumed.set_cookie("session", cookie.value)
    assert b"Harbor Blue" in resumed.get("/palette").data


def test_friendly_errors_and_csrf(client):
    assert client.get("/missing-page").status_code == 404
    response = client.post("/palette/clear")
    assert response.status_code == 400 and b"security token" in response.data
    assert client.post("/admin/login", data={"username": "anything", "password": "anything"}).status_code == 400
    assert client.get("/palette/clear").status_code == 405
