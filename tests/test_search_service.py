# tests/test_search_service.py

from backend.services.search_service import (
    normalize,
    lexical_score,
    chroma_distance_to_score,
    score_label,
    SCORE_EXACT,
    SCORE_NORMALIZED,
    SCORE_PREFIX,
    SCORE_SUBSTRING,
    SCORE_SEMANTIC_MAX,
    MIN_SCORE,
)


# ── normalize() ───────────────────────────────────────────────────────────────

def test_normalize_empty_string():
    assert normalize("") == ""

def test_normalize_strips_punctuation():
    assert normalize("Ssebo!") == "ssebo"

def test_normalize_lowercases():
    assert normalize("Good Morning") == "good morning"

def test_normalize_collapses_whitespace():
    assert normalize("  good  morning  ") == "good morning"

def test_normalize_removes_trailing_whitespace():
    assert normalize("hello ") == "hello"

def test_normalize_handles_period():
    assert normalize("Good morning.") == "good morning"
