# tests/test_admin_degradation.py

"""
Admin endpoint degradation tests.
Verify that /api/v1/admin/status always returns 200 and never raises,
even when ChromaDB, feedback files, or training files are unavailable.
"""

from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_admin_status_always_returns_200():
    """Baseline: endpoint is reachable and returns 200."""
    response = client.get("/api/v1/admin/status")
    assert response.status_code == 200


def test_admin_status_returns_ok_api_status():
    """api_status is always 'ok' — never changes based on subsystem health."""
    response = client.get("/api/v1/admin/status")
    assert response.json()["system"]["api_status"] == "ok"


def test_admin_status_chroma_disconnected_still_returns_200():
    """ChromaDB failure degrades gracefully — does not crash the endpoint."""
    with patch("backend.api.routes.admin._chroma_connected", return_value=False), \
         patch("backend.api.routes.admin._collection_counts", return_value={
             "vocabulary": 0, "sentences": 0, "grammar": 0, "proverbs": 0, "total": 0
         }):
        response = client.get("/api/v1/admin/status")
    assert response.status_code == 200
    data = response.json()
    assert data["system"]["chroma_connected"] is False
    assert data["collections"]["total"] == 0


def test_admin_status_tts_deps_absent_still_returns_200():
    """Missing TTS dependencies degrade gracefully."""
    with patch("backend.api.routes.admin._tts_deps_installed", return_value=False):
        response = client.get("/api/v1/admin/status")
    assert response.status_code == 200
    assert response.json()["system"]["tts_deps_installed"] is False


def test_admin_status_openrouter_key_not_set():
    """openrouter_key_set reflects whether the key is configured."""
    with patch("backend.api.routes.admin.settings") as mock_settings:
        mock_settings.openrouter_api_key = ""
        response = client.get("/api/v1/admin/status")
    assert response.status_code == 200
    assert response.json()["system"]["openrouter_key_set"] is False


def test_admin_status_openrouter_key_set():
    """openrouter_key_set is True when the key is present."""
    with patch("backend.api.routes.admin.settings") as mock_settings:
        mock_settings.openrouter_api_key = "sk-test-key"
        response = client.get("/api/v1/admin/status")
    assert response.status_code == 200
    assert response.json()["system"]["openrouter_key_set"] is True


def test_admin_status_feedback_section_non_negative():
    """All feedback counts must be non-negative integers."""
    response = client.get("/api/v1/admin/status")
    fb = response.json()["feedback"]
    for key in ("total_submissions", "correct", "wrong", "needs_review"):
        assert isinstance(fb[key], int)
        assert fb[key] >= 0


def test_admin_status_training_section_non_negative():
    """Training pair counts must be non-negative integers."""
    response = client.get("/api/v1/admin/status")
    tr = response.json()["training"]
    for key in ("training_pairs", "correction_pairs"):
        assert isinstance(tr[key], int)
        assert tr[key] >= 0


def test_admin_status_collections_total_equals_sum():
    """Total collection count must equal the sum of individual counts."""
    response = client.get("/api/v1/admin/status")
    cols = response.json()["collections"]
    expected_total = cols["vocabulary"] + cols["sentences"] + cols["grammar"] + cols["proverbs"]
    assert cols["total"] == expected_total


def test_admin_status_pipeline_section_nllb_is_bool():
    """nllb_loaded must be a boolean."""
    response = client.get("/api/v1/admin/status")
    pl = response.json()["pipeline"]
    assert isinstance(pl["nllb_loaded"], bool)
