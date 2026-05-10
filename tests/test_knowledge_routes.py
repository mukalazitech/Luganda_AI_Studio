# tests/test_knowledge_routes.py

import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ── GET /api/v1/knowledge/search ──────────────────────────────────────────────

def test_search_valid_query_returns_200(client):
    response = client.get("/api/v1/knowledge/search", params={"q": "hello"})
    assert response.status_code == 200

def test_search_response_has_required_keys(client):
    response = client.get("/api/v1/knowledge/search", params={"q": "hello"})
    data = response.json()
    assert "query" in data
    assert "collection" in data
    assert "total" in data
    assert "results" in data

def test_search_query_echoed_in_response(client):
    response = client.get("/api/v1/knowledge/search", params={"q": "ssebo"})
    data = response.json()
    assert data["query"] == "ssebo"

def test_search_empty_query_returns_400(client):
    response = client.get("/api/v1/knowledge/search", params={"q": ""})
    assert response.status_code in (400, 422)

def test_search_query_too_long_returns_422(client):
    long_query = "a" * 201
    response = client.get("/api/v1/knowledge/search", params={"q": long_query})
    assert response.status_code == 422

def test_search_top_k_limits_results(client):
    response = client.get("/api/v1/knowledge/search", params={"q": "hello", "top_k": 3})
    data = response.json()
    assert len(data["results"]) <= 3

def test_search_collection_filter_vocabulary(client):
    response = client.get(
        "/api/v1/knowledge/search",
        params={"q": "hello", "collection": "vocabulary"},
    )
    data = response.json()
    assert response.status_code == 200
    for result in data["results"]:
        assert result["metadata"].get("_collection") == "vocabulary"

def test_search_invalid_collection_returns_200_empty(client):
    response = client.get(
        "/api/v1/knowledge/search",
        params={"q": "hello", "collection": "nonexistent_collection"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["results"] == []


# ── GET /api/v1/knowledge/status ──────────────────────────────────────────────

def test_status_returns_200(client):
    response = client.get("/api/v1/knowledge/status")
    assert response.status_code == 200

def test_status_has_required_keys(client):
    response = client.get("/api/v1/knowledge/status")
    data = response.json()
    assert "collections" in data
    assert "total_documents" in data

def test_status_contains_all_core_collections(client):
    response = client.get("/api/v1/knowledge/status")
    data = response.json()
    collections = data["collections"]
    for name in ("vocabulary", "sentences", "grammar", "proverbs"):
        assert name in collections, f"Missing collection: {name}"

def test_status_counts_are_non_negative_integers(client):
    response = client.get("/api/v1/knowledge/status")
    data = response.json()
    for name, count in data["collections"].items():
        assert isinstance(count, int), f"{name} count is not an int"
        assert count >= 0, f"{name} count is negative"

def test_status_total_documents_matches_sum(client):
    response = client.get("/api/v1/knowledge/status")
    data = response.json()
    expected_total = sum(v for v in data["collections"].values() if v >= 0)
    assert data["total_documents"] == expected_total
