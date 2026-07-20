"""Read-only curated JSON library API route tests."""


def test_proverbs_returns_normalized_entries(client):
    response = client.get("/api/v1/library/proverbs")

    assert response.status_code == 200
    data = response.json()
    assert data["collection"] == "proverbs"
    assert data["entries"]
    assert data["count"] == len(data["entries"])
    assert {"id", "luganda", "english", "meaning", "theme"} <= data["entries"][0].keys()


def test_phrases_returns_normalized_entries(client):
    response = client.get("/api/v1/library/phrases")

    assert response.status_code == 200
    data = response.json()
    assert data["collection"] == "phrases"
    assert data["entries"]
    assert data["count"] == len(data["entries"])
    assert {"id", "luganda", "english", "topic", "difficulty"} <= data["entries"][0].keys()


def test_vocabulary_returns_entries_with_stable_keys(client):
    first_response = client.get("/api/v1/library/vocabulary")
    second_response = client.get("/api/v1/library/vocabulary")

    assert first_response.status_code == 200
    data = first_response.json()
    assert data["collection"] == "vocabulary"
    assert data["entries"]
    assert data["count"] == len(data["entries"])
    assert {
        "key",
        "luganda",
        "english",
        "category",
        "part_of_speech",
        "example_luganda",
        "example_english",
    } <= data["entries"][0].keys()
    assert all("example_sentence_luganda" not in entry for entry in data["entries"])
    assert all("example_sentence_english" not in entry for entry in data["entries"])
    assert [entry["key"] for entry in data["entries"]] == [
        entry["key"] for entry in second_response.json()["entries"]
    ]


def test_grammar_returns_all_seven_normalized_sections(client):
    response = client.get("/api/v1/library/grammar")

    assert response.status_code == 200
    data = response.json()
    assert data["collection"] == "grammar"
    assert data["count"] == len(data["sections"]) == 7
    assert all({"id", "title", "kind", "items"} <= section.keys() for section in data["sections"])
    sections = {section["id"]: section for section in data["sections"]}
    assert {section_id: section["kind"] for section_id, section in sections.items()} == {
        "consonants:rules": "rules",
        "verb_tenses:tenses": "tenses",
        "verb_tenses:tense_summary_table": "tense_summary_table",
        "verb_tenses:subject_prefixes": "subject_prefixes",
        "vowels:rules": "rules",
        "word_classes:word_classes": "word_classes",
        "word_classes:question_words": "question_words",
    }
    assert {section_id: section["title"] for section_id, section in sections.items()} == {
        "consonants:rules": "Consonants",
        "verb_tenses:tenses": "Verb Tenses — Tenses",
        "verb_tenses:tense_summary_table": "Verb Tenses — Tense Summary Table",
        "verb_tenses:subject_prefixes": "Verb Tenses — Subject Prefixes",
        "vowels:rules": "Vowels",
        "word_classes:word_classes": "Word Classes — Word Classes",
        "word_classes:question_words": "Word Classes — Question Words",
    }
    titles = [section["title"] for section in data["sections"]]
    assert len(titles) == len(set(titles))


def test_proverbs_count_only_returns_no_entries(client):
    response = client.get("/api/v1/library/proverbs", params={"count_only": "true"})

    assert response.status_code == 200
    assert response.json() == {"collection": "proverbs", "count": 60}


def test_grammar_count_only_returns_no_sections(client):
    response = client.get("/api/v1/library/grammar", params={"count_only": "true"})

    assert response.status_code == 200
    assert response.json() == {"collection": "grammar", "count": 7}


def test_unknown_library_collection_returns_404(client):
    response = client.get("/api/v1/library/recipes")

    assert response.status_code == 404
