# tests/test_events_route.py
import json
import pytest


@pytest.fixture
def events_file(tmp_path, monkeypatch):
    from backend.api.routes import events as ev
    f = tmp_path / "events.jsonl"
    monkeypatch.setattr(ev, "EVENTS_FILE", f)
    return f


VALID = {"session": "3f2b8c1e-aaaa-bbbb-cccc-0123456789ab", "event": "collection_opened", "target": "proverbs"}


def test_valid_event_appends_one_line(client, events_file):
    r = client.post("/api/v1/events", json=VALID)
    assert r.status_code == 200
    lines = events_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert set(rec) == {"session", "event", "target", "ts"}   # nothing else is ever stored


def test_unknown_event_rejected(client, events_file):
    r = client.post("/api/v1/events", json={**VALID, "event": "typed_translation"})
    assert r.status_code == 422


def test_free_text_target_rejected(client, events_file):
    r = client.post("/api/v1/events", json={**VALID, "target": "how do I say I love you"})
    assert r.status_code == 422          # spaces/length -> not an identifier


def test_extra_fields_rejected(client, events_file):
    r = client.post("/api/v1/events", json={**VALID, "text": "oli otya"})
    assert r.status_code == 422          # extra=forbid blocks smuggling learner text


def test_bad_session_rejected(client, events_file):
    r = client.post("/api/v1/events", json={**VALID, "session": "patrick@gmail.com"})
    assert r.status_code == 422
