from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_cards_response_includes_category_field():
    """Every flash card must expose a `category` field (may be empty string)."""
    res = client.get("/api/v1/teach/cards?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert data["cards"], "expected at least one card"
    for card in data["cards"]:
        assert "category" in card, "each card must include a 'category' key"
        assert isinstance(card["category"], str)


def test_fallback_animal_card_has_animals_category():
    """When ChromaDB is empty the fallback set is used; its animal rows
    must carry category='animals' so the UI shows the right icon.
    Embwa (Dog) is a fallback animal row."""
    res = client.get("/api/v1/teach/cards?limit=50&shuffle=false")
    assert res.status_code == 200
    cards = res.json()["cards"]
    embwa = next((c for c in cards if c["luganda"] == "Embwa"), None)
    # Only asserted when fallback data is in play (Embwa present).
    if embwa is not None:
        assert embwa["category"] == "animals"
