from backend.services.translation import service
from backend.services.translation.schemas import TranslationRequest


class _FakeCollection:
    def __init__(self, metadatas):
        self._metadatas = metadatas

    def get(self, include):
        assert include == ["metadatas"]
        return {"metadatas": self._metadatas}


class _FakeChroma:
    def __init__(self, collections):
        self._collections = collections

    def get_collection(self, name):
        return _FakeCollection(self._collections.get(name, []))


def test_partial_matching_handles_punctuation_in_curated_greetings(monkeypatch):
    monkeypatch.setattr(
        service,
        "chroma_client",
        _FakeChroma(
            {
                "sentences": [
                    {
                        "english": "Hello! / Welcome in.",
                        "luganda": "Koodi! / Kalibu.",
                        "source_file": "greetings.json",
                        "verified": True,
                    }
                ]
            }
        ),
    )

    result = service._scan_collection(
        "sentences",
        source_field="english",
        target_field="luganda",
        input_text="hello",
    )

    assert result["translated_text"] == "Koodi! / Kalibu."
    assert result["match_type"] == "partial"


def test_single_word_does_not_return_a_sentence_containing_that_word(monkeypatch):
    monkeypatch.setattr(
        service,
        "chroma_client",
        _FakeChroma(
            {
                "sentences": [
                    {
                        "luganda": (
                            "Oluvannyuma lw'okukkirizibwa, ekiwandiiko kyatwalibwa "
                            "ku duuka erikuba ebitabo."
                        ),
                        "english": (
                            "After its adoption, the handwritten draft was sent "
                            "to a printing shop several blocks away."
                        ),
                        "source_file": "flores_sentences.json",
                    }
                ]
            }
        ),
    )

    result = service._scan_collection(
        "sentences",
        source_field="luganda",
        target_field="english",
        input_text="duuka",
    )

    assert result is None


def test_single_word_can_match_a_short_vocabulary_variant(monkeypatch):
    monkeypatch.setattr(
        service,
        "chroma_client",
        _FakeChroma(
            {
                "vocabulary": [
                    {
                        "luganda": "edduuka",
                        "english": "shop",
                        "source_file": "all_vocabulary.json",
                    }
                ]
            }
        ),
    )

    result = service._scan_collection(
        "vocabulary",
        source_field="luganda",
        target_field="english",
        input_text="duuka",
    )

    assert result["translated_text"] == "shop"
    assert result["match_type"] == "partial"


def test_low_confidence_semantic_candidate_is_not_authoritative_success(monkeypatch):
    monkeypatch.setattr(service, "_scan_collection", lambda **kwargs: None)
    monkeypatch.setattr(
        service,
        "_try_semantic_match",
        lambda collection_name, **kwargs: (
            {
                "translated_text": "laba!",
                "match_type": "semantic",
                "confidence": 0.6206,
                "matched_collection": collection_name,
                "matched_source_file": "groupB_dictionary.csv",
            }
            if collection_name == "vocabulary"
            else None
        ),
    )

    result = service.translate(
        TranslationRequest(text="hello", direction="en_to_lg")
    )

    assert result.status == "possible_match"
    assert result.match_type == "semantic"
    assert result.confidence == 0.6206
    assert result.matched_source_file == "groupB_dictionary.csv"


def test_curated_exact_match_wins_tie_against_imported_exact_match(monkeypatch):
    monkeypatch.setattr(
        service,
        "chroma_client",
        _FakeChroma(
            {
                "vocabulary": [
                    {
                        "english": "hello",
                        "luganda": "laba!",
                        "source_file": "groupB_dictionary.csv",
                    }
                ],
                "sentences": [
                    {
                        "english": "hello",
                        "luganda": "Koodi! / Kalibu.",
                        "source_file": "greetings.json",
                        "verified": True,
                    }
                ],
            }
        ),
    )

    result = service.translate(
        TranslationRequest(text="hello", direction="en_to_lg")
    )

    assert result.status == "success"
    assert result.translated_text == "Koodi! / Kalibu."
    assert result.matched_source_file == "greetings.json"
    assert result.trust_tier == "curated"
