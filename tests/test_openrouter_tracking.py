"""
Test suite for OpenRouter last_call_at timestamp tracking.

Verifies that the openrouter_service module correctly tracks
when the last successful OpenRouter translation call was made.
"""

from backend.services.translation import openrouter_service as svc


def test_last_call_at_starts_as_none():
    """_last_call_at should be None until a successful translation occurs."""
    # Reset state for isolation
    svc._last_call_at = None
    assert svc.get_last_call_at() is None


def test_get_last_call_at_returns_string_after_set():
    """get_last_call_at() should return the ISO 8601 timestamp when set."""
    svc._last_call_at = "2026-05-10T12:00:00+00:00"
    assert svc.get_last_call_at() == "2026-05-10T12:00:00+00:00"
    svc._last_call_at = None  # clean up
