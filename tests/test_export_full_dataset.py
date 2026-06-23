import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.export_full_dataset import (
    build_dataset,
    extract_grammar_rules_entries,
    extract_proverb_entries,
    extract_verb_tenses_entries,
    extract_vocabulary_or_sentence_entries,
    extract_word_classes_entries,
    write_export,
)


def test_extract_vocabulary_entries_basic():
    data = {
        "entries": [
            {"luganda": "Embwa", "english": "Dog", "category": "animals", "needs_review": False},
            {"luganda": "Embuzi", "english": "Goat", "category": "animals", "needs_review": False},
        ]
    }
    rows = extract_vocabulary_or_sentence_entries(data, row_type="vocabulary")
    assert rows == [
        {"luganda": "Embwa", "english": "Dog", "type": "vocabulary", "category": "animals", "notes": None},
        {"luganda": "Embuzi", "english": "Goat", "type": "vocabulary", "category": "animals", "notes": None},
    ]


def test_extract_vocabulary_entries_skips_needs_review():
    data = {
        "entries": [
            {"luganda": "Eddubu", "english": "Bear", "category": "animals", "needs_review": True},
            {"luganda": "Engo", "english": "Leopard", "category": "animals", "needs_review": False},
        ]
    }
    rows = extract_vocabulary_or_sentence_entries(data, row_type="vocabulary")
    assert len(rows) == 1
    assert rows[0]["luganda"] == "Engo"


def test_extract_sentence_entries_basic():
    data = {
        "entries": [
            {
                "id": "dl_001",
                "english": "I go to work every day.",
                "luganda": "Ngenda ku mulimu buli lunaku.",
                "tense": "everyday",
                "topic": "work",
                "difficulty": "beginner",
                "needs_review": False,
            }
        ]
    }
    rows = extract_vocabulary_or_sentence_entries(data, row_type="sentence")
    assert rows == [
        {
            "luganda": "Ngenda ku mulimu buli lunaku.",
            "english": "I go to work every day.",
            "type": "sentence",
            "category": "work",
            "notes": None,
        }
    ]


def test_extract_proverb_entries_basic():
    data = {
        "entries": [
            {
                "id": "prov_001",
                "luganda": "Kyosimba onanya kyoolyako etooke",
                "english": "You reap what you sow.",
                "theme": "hardwork",
                "meaning": "Whatever you plant without care is what you benefit from.",
                "needs_review": False,
            }
        ]
    }
    rows = extract_proverb_entries(data)
    assert rows == [
        {
            "luganda": "Kyosimba onanya kyoolyako etooke",
            "english": "You reap what you sow.",
            "type": "proverb",
            "category": "proverbs",
            "notes": "[hardwork] Whatever you plant without care is what you benefit from.",
        }
    ]


def test_extract_proverb_entries_skips_needs_review():
    data = {
        "entries": [
            {"luganda": "X", "english": "Y", "theme": "t", "meaning": "m", "needs_review": True},
        ]
    }
    assert extract_proverb_entries(data) == []


def test_extract_grammar_rules_entries_basic():
    data = {
        "metadata": {"category": "grammar_consonants"},
        "rules": [
            {
                "rule_id": "con_001",
                "rule_name": "Luganda Consonants Are Similar to English",
                "explanation": "Luganda uses almost all the same consonants as English.",
                "needs_review": False,
            }
        ],
    }
    rows = extract_grammar_rules_entries(data)
    assert rows == [
        {
            "luganda": "Luganda Consonants Are Similar to English",
            "english": "Luganda uses almost all the same consonants as English.",
            "type": "grammar",
            "category": "grammar_consonants",
            "notes": "Luganda uses almost all the same consonants as English.",
        }
    ]


def test_extract_grammar_rules_entries_skips_needs_review():
    data = {
        "metadata": {"category": "grammar_vowels"},
        "rules": [
            {"rule_id": "vow_999", "rule_name": "X", "explanation": "Y", "needs_review": True},
        ],
    }
    assert extract_grammar_rules_entries(data) == []


def test_extract_verb_tenses_entries_basic():
    data = {
        "metadata": {"category": "grammar_verb_tenses"},
        "tenses": [
            {
                "tense_id": "t_001",
                "english_name": "Everyday / Habitual Tense",
                "description": "Used for actions that happen regularly.",
                "examples": [
                    {
                        "english_verb": "eat",
                        "luganda_infinitive": "okulya",
                        "everyday_form": "alya",
                        "english_everyday": "he/she eats (every day)",
                    }
                ],
                "sentence_examples": [
                    {"luganda": "Ngenda ku mulimu buli lunaku.", "english": "I go to work every day."}
                ],
                "needs_review": False,
            }
        ],
    }
    rows = extract_verb_tenses_entries(data)
    assert rows == [
        {
            "luganda": "okulya",
            "english": "he/she eats (every day)",
            "type": "grammar",
            "category": "grammar_verb_tenses",
            "notes": "Used for actions that happen regularly.",
        },
        {
            "luganda": "Ngenda ku mulimu buli lunaku.",
            "english": "I go to work every day.",
            "type": "grammar",
            "category": "grammar_verb_tenses",
            "notes": "Used for actions that happen regularly.",
        },
    ]


def test_extract_verb_tenses_entries_skips_needs_review_tense():
    data = {
        "metadata": {"category": "grammar_verb_tenses"},
        "tenses": [
            {
                "tense_id": "t_999",
                "description": "desc",
                "examples": [{"luganda_infinitive": "x", "english_everyday": "y"}],
                "sentence_examples": [{"luganda": "a", "english": "b"}],
                "needs_review": True,
            }
        ],
    }
    assert extract_verb_tenses_entries(data) == []


def test_extract_word_classes_entries_basic():
    data = {
        "word_classes": [
            {
                "class_id": "wc_001",
                "description": "Doing words.",
                "examples": [{"luganda": "kufumba", "english": "to cook"}],
                "needs_review": False,
            }
        ],
        "question_words": {
            "entries": [
                {"luganda": "Lwaki?", "english": "Why?", "example": "Lwaki ogenda? = Why are you going?", "needs_review": False}
            ]
        },
    }
    rows = extract_word_classes_entries(data)
    assert rows == [
        {
            "luganda": "kufumba",
            "english": "to cook",
            "type": "grammar",
            "category": "grammar_word_classes",
            "notes": "Doing words.",
        },
        {
            "luganda": "Lwaki?",
            "english": "Why?",
            "type": "grammar",
            "category": "grammar_question_words",
            "notes": "Lwaki ogenda? = Why are you going?",
        },
    ]


def test_extract_word_classes_entries_skips_needs_review():
    data = {
        "word_classes": [
            {"description": "d", "examples": [{"luganda": "x", "english": "y"}], "needs_review": True}
        ],
        "question_words": {
            "entries": [{"luganda": "a", "english": "b", "example": "c", "needs_review": True}]
        },
    }
    assert extract_word_classes_entries(data) == []


def test_build_dataset_combines_all_sources(tmp_path):
    (tmp_path / "vocabulary").mkdir()
    (tmp_path / "vocabulary" / "animals.json").write_text(
        json.dumps({"entries": [{"luganda": "Embwa", "english": "Dog", "category": "animals", "needs_review": False}]}),
        encoding="utf-8",
    )
    (tmp_path / "sentences").mkdir()
    (tmp_path / "sentences" / "greetings.json").write_text(
        json.dumps({"entries": [{"luganda": "Wasuze otya?", "english": "Good morning.", "topic": "greetings", "needs_review": False}]}),
        encoding="utf-8",
    )
    (tmp_path / "proverbs").mkdir()
    (tmp_path / "proverbs" / "kiganda_proverbs.json").write_text(
        json.dumps({"entries": [{"luganda": "P", "english": "E", "theme": "t", "meaning": "m", "needs_review": False}]}),
        encoding="utf-8",
    )
    (tmp_path / "grammar").mkdir()
    (tmp_path / "grammar" / "consonants.json").write_text(
        json.dumps({"metadata": {"category": "grammar_consonants"}, "rules": [{"rule_name": "R", "explanation": "X", "needs_review": False}]}),
        encoding="utf-8",
    )

    rows = build_dataset(tmp_path)
    types = sorted(r["type"] for r in rows)
    assert types == ["grammar", "proverb", "sentence", "vocabulary"]
    assert len(rows) == 4


def test_write_export_writes_jsonl(tmp_path):
    rows = [{"luganda": "a", "english": "b", "type": "vocabulary", "category": "c", "notes": None}]
    output_path = write_export(rows, tmp_path, today="2026-06-23")
    assert output_path == tmp_path / "full_dataset_export_2026-06-23.jsonl"
    lines = output_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1
    assert json.loads(lines[0]) == rows[0]
