import os
import sys
import pytest
from unittest.mock import MagicMock
from flask import jsonify
import importlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import models


@pytest.fixture
def client(monkeypatch):
    """Flask test client with templates rendered as JSON."""
    mock_db = MagicMock()
    monkeypatch.setattr(models, "DB", lambda: mock_db)
    import server
    importlib.reload(server)
    monkeypatch.setattr(
        server, "render_template", lambda *args, **kwargs: jsonify(kwargs["data"])
    )
    server.app.config["TESTING"] = True
    with server.app.test_client() as client_app:
        yield client_app, mock_db


def test_get_lesson_valid(client):
    client_app, mock_db = client
    mock_db.get_lessons_list.return_value = [
        {"id": 0, "title": "L0", "desc": "", "image": ""},
        {"id": 1, "title": "L1", "desc": "", "image": ""},
    ]
    mock_db.get_lesson_data.return_value = {
        "id": 1,
        "url": "http://example.com/lesson1",
    }

    response = client_app.get("/course/1/lesson/1")

    assert response.status_code == 200
    assert response.get_json() == {"id": 1, "url": "http://example.com/lesson1"}


def test_get_lesson_invalid(client):
    client_app, mock_db = client
    mock_db.get_lessons_list.return_value = [
        {"id": 0, "title": "L0", "desc": "", "image": ""}
    ]
    mock_db.get_lesson_data.return_value = {
        "id": 99,
        "url": "http://example.com/lesson",
    }

    response = client_app.get("/course/1/lesson/99")

    assert response.status_code == 200
    assert response.get_json() == {"id": 0, "url": "http://example.com/lesson"}

