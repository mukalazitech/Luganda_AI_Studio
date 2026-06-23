# Luganda Vocabulary/Sentence/Grammar/Proverb HuggingFace Dataset — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Export the 12 vocabulary + 2 sentence + 4 grammar + 1 proverb source JSON files in `datasets/` into one flat JSONL with a unified `luganda`/`english`/`type`/`category`/`notes` schema, then push it to a new HuggingFace dataset repo `MukalaziPatrick/luganda-vocabulary-dataset`.

**Architecture:** Two standalone scripts mirroring the existing `export_dataset.py` / `upload_to_huggingface.py` pattern. `export_full_dataset.py` reads the raw `datasets/` JSON tree (not ChromaDB, not the correction-pairs pipeline) and writes `data/training/full_dataset_export_YYYY-MM-DD.jsonl`. `upload_full_dataset_to_huggingface.py` loads the latest such file and pushes it via `huggingface_hub`/`datasets`, reusing the already-authenticated `hf` CLI session.

**Tech Stack:** Python 3.11, `huggingface_hub`, `datasets` (both already installed in venv), pytest.

---

## File Structure

- Create: `scripts/export_full_dataset.py` — reads `datasets/{vocabulary,sentences,grammar,proverbs}/*.json`, normalizes to the unified schema, writes JSONL.
- Create: `tests/test_export_full_dataset.py` — unit tests for each per-type extractor function using small inline fixture dicts (no dependency on the real `datasets/` files, so tests stay stable if source data changes).
- Create: `scripts/upload_full_dataset_to_huggingface.py` — loads latest export, uploads to HF Hub with a dataset card.

## Unified row schema (reference for every task below)

```python
{
    "luganda": str,
    "english": str,
    "type": str,      # "vocabulary" | "sentence" | "grammar" | "proverb"
    "category": str,
    "notes": str | None,
}
```

---

### Task 1: Vocabulary and sentence extractors (the simple, shared shape)

**Files:**
- Create: `scripts/export_full_dataset.py`
- Test: `tests/test_export_full_dataset.py`

Both `datasets/vocabulary/*.json` and `datasets/sentences/*.json` share the same entry shape: top-level `entries: []`, each entry has `luganda`, `english`, `category`, `needs_review`. Vocabulary entries additionally have `example_sentence_luganda`/`example_sentence_english` (unused for `notes` — there is no separate short note field, so vocabulary/sentence rows get `notes=None`).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_export_full_dataset.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.export_full_dataset import extract_vocabulary_or_sentence_entries


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
```

Note: sentence entries use `topic` (not `category`) as their grouping field — `extract_vocabulary_or_sentence_entries` must read `category` if present, else fall back to `topic`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_export_full_dataset.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.export_full_dataset'` (file doesn't exist yet).

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/export_full_dataset.py

"""
Export the curated vocabulary/sentence/grammar/proverb corpus from datasets/
into one flat JSONL with a unified schema, for HuggingFace upload.

This is separate from scripts/export_dataset.py, which exports user-submitted
correction pairs (a different, much smaller dataset).

Reads:
  datasets/vocabulary/*.json
  datasets/sentences/*.json
  datasets/grammar/*.json
  datasets/proverbs/*.json

Writes:
  data/training/full_dataset_export_YYYY-MM-DD.jsonl

Usage:
  python scripts/export_full_dataset.py
  python scripts/export_full_dataset.py --dry-run
"""

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATASETS_DIR = PROJECT_ROOT / "datasets"
OUTPUT_DIR = PROJECT_ROOT / "data" / "training"


def extract_vocabulary_or_sentence_entries(data: dict, row_type: str) -> list[dict]:
    """Extract rows from a vocabulary/*.json or sentences/*.json file's entries[]."""
    rows = []
    for entry in data.get("entries", []):
        if entry.get("needs_review"):
            continue
        luganda = entry.get("luganda")
        english = entry.get("english")
        if not luganda or not english:
            continue
        category = entry.get("category") or entry.get("topic") or ""
        rows.append(
            {
                "luganda": luganda,
                "english": english,
                "type": row_type,
                "category": category,
                "notes": None,
            }
        )
    return rows


def main():
    parser = argparse.ArgumentParser(description="Export full vocabulary/sentence/grammar/proverb dataset")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()
    print("Task 1 placeholder main — extended in later tasks")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_export_full_dataset.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/export_full_dataset.py tests/test_export_full_dataset.py
git commit -m "feat: vocabulary/sentence extractor for full dataset export"
```

---

### Task 2: Proverb extractor

**Files:**
- Modify: `scripts/export_full_dataset.py`
- Test: `tests/test_export_full_dataset.py`

Proverbs (`datasets/proverbs/kiganda_proverbs.json`) have `entries: []` with `luganda`, `english`, `theme`, `meaning`, `needs_review`. `notes` = `"[theme] meaning"` when both present, else whichever is present, else `None`.

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_export_full_dataset.py
from scripts.export_full_dataset import extract_proverb_entries


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_export_full_dataset.py -v -k proverb`
Expected: FAIL with `ImportError: cannot import name 'extract_proverb_entries'`

- [ ] **Step 3: Write minimal implementation**

Add to `scripts/export_full_dataset.py` (after `extract_vocabulary_or_sentence_entries`):

```python
def extract_proverb_entries(data: dict) -> list[dict]:
    """Extract rows from proverbs/*.json's entries[]."""
    rows = []
    for entry in data.get("entries", []):
        if entry.get("needs_review"):
            continue
        luganda = entry.get("luganda")
        english = entry.get("english")
        if not luganda or not english:
            continue
        theme = entry.get("theme")
        meaning = entry.get("meaning")
        if theme and meaning:
            notes = f"[{theme}] {meaning}"
        else:
            notes = meaning or theme or None
        rows.append(
            {
                "luganda": luganda,
                "english": english,
                "type": "proverb",
                "category": "proverbs",
                "notes": notes,
            }
        )
    return rows
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_export_full_dataset.py -v -k proverb`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/export_full_dataset.py tests/test_export_full_dataset.py
git commit -m "feat: proverb extractor for full dataset export"
```

---

### Task 3: Grammar — rules[] extractor (consonants.json, vowels.json)

**Files:**
- Modify: `scripts/export_full_dataset.py`
- Test: `tests/test_export_full_dataset.py`

Per the design decision: one row per *rule*, not per example (examples have inconsistent inner keys across rules — e.g. `con_003`'s examples use `single_form`/`double_form`, `vow_001`'s use `luganda_example`/`english_meaning` — too irregular to flatten safely). `luganda` = `rule_name`, `english` = `explanation`, `notes` = `explanation` (same text — there's no separate short gloss for a grammar rule), `category` = `"grammar_consonants"` or `"grammar_vowels"` (passed in as a parameter since the file itself doesn't carry a clean category string in `rules[]` — `consonants.json`/`vowels.json`'s top-level `metadata.category` does, e.g. `"grammar_consonants"`).

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_export_full_dataset.py
from scripts.export_full_dataset import extract_grammar_rules_entries


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_export_full_dataset.py -v -k grammar_rules`
Expected: FAIL with `ImportError: cannot import name 'extract_grammar_rules_entries'`

- [ ] **Step 3: Write minimal implementation**

Add to `scripts/export_full_dataset.py`:

```python
def extract_grammar_rules_entries(data: dict) -> list[dict]:
    """Extract rows from grammar files with a top-level rules[] (consonants, vowels).

    One row per rule (not per example) — example sub-structures are inconsistent
    across rules and cannot be flattened to luganda/english safely.
    """
    category = data.get("metadata", {}).get("category", "")
    rows = []
    for rule in data.get("rules", []):
        if rule.get("needs_review"):
            continue
        rule_name = rule.get("rule_name")
        explanation = rule.get("explanation")
        if not rule_name or not explanation:
            continue
        rows.append(
            {
                "luganda": rule_name,
                "english": explanation,
                "type": "grammar",
                "category": category,
                "notes": explanation,
            }
        )
    return rows
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_export_full_dataset.py -v -k grammar_rules`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/export_full_dataset.py tests/test_export_full_dataset.py
git commit -m "feat: grammar rules[] extractor (one row per rule) for full dataset export"
```

---

### Task 4: Grammar — verb_tenses.json extractor

**Files:**
- Modify: `scripts/export_full_dataset.py`
- Test: `tests/test_export_full_dataset.py`

`verb_tenses.json` has top-level `tenses: []`. Each tense has `needs_review` gating **both** its `examples[]` and `sentence_examples[]`. `examples[]` items have `luganda_infinitive`/`english_everyday` (not a clean 1:1 luganda/english pair — `luganda_infinitive` is the infinitive form, `english_everyday` is the conjugated-tense English gloss; still usable as the row's luganda/english since both are real Luganda/English text). `sentence_examples[]` items have `luganda`/`english` directly. `notes` = tense's `description`. `category` = `"grammar_verb_tenses"` (from `metadata.category`).

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_export_full_dataset.py
from scripts.export_full_dataset import extract_verb_tenses_entries


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_export_full_dataset.py -v -k verb_tenses`
Expected: FAIL with `ImportError: cannot import name 'extract_verb_tenses_entries'`

- [ ] **Step 3: Write minimal implementation**

Add to `scripts/export_full_dataset.py`:

```python
def extract_verb_tenses_entries(data: dict) -> list[dict]:
    """Extract rows from grammar/verb_tenses.json's tenses[]."""
    category = data.get("metadata", {}).get("category", "")
    rows = []
    for tense in data.get("tenses", []):
        if tense.get("needs_review"):
            continue
        notes = tense.get("description")
        for example in tense.get("examples", []):
            luganda = example.get("luganda_infinitive")
            english = example.get("english_everyday")
            if not luganda or not english:
                continue
            rows.append(
                {"luganda": luganda, "english": english, "type": "grammar", "category": category, "notes": notes}
            )
        for sentence in tense.get("sentence_examples", []):
            luganda = sentence.get("luganda")
            english = sentence.get("english")
            if not luganda or not english:
                continue
            rows.append(
                {"luganda": luganda, "english": english, "type": "grammar", "category": category, "notes": notes}
            )
    return rows
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_export_full_dataset.py -v -k verb_tenses`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/export_full_dataset.py tests/test_export_full_dataset.py
git commit -m "feat: verb_tenses extractor for full dataset export"
```

---

### Task 5: Grammar — word_classes.json extractor (word_classes[] + question_words)

**Files:**
- Modify: `scripts/export_full_dataset.py`
- Test: `tests/test_export_full_dataset.py`

`word_classes.json` has two top-level sections: `word_classes: []` (each with `examples: []` of `{luganda, english}`, `description`, `needs_review`) and `question_words: {"entries": [...]}` (a dict, not a list — each entry has `luganda`, `english`, `example`, `needs_review` directly, no wrapping rule object). `category` = `"grammar_word_classes"` for word_classes rows, `"grammar_question_words"` for question_words rows (both literal strings — this file's `metadata.category` is just `"grammar_word_classes"` overall, so question_words rows use a distinct literal to keep the two groups separable in the dataset).

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_export_full_dataset.py
from scripts.export_full_dataset import extract_word_classes_entries


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_export_full_dataset.py -v -k word_classes`
Expected: FAIL with `ImportError: cannot import name 'extract_word_classes_entries'`

- [ ] **Step 3: Write minimal implementation**

Add to `scripts/export_full_dataset.py`:

```python
def extract_word_classes_entries(data: dict) -> list[dict]:
    """Extract rows from grammar/word_classes.json's word_classes[] and question_words.entries[]."""
    rows = []
    for word_class in data.get("word_classes", []):
        if word_class.get("needs_review"):
            continue
        notes = word_class.get("description")
        for example in word_class.get("examples", []):
            luganda = example.get("luganda")
            english = example.get("english")
            if not luganda or not english:
                continue
            rows.append(
                {
                    "luganda": luganda,
                    "english": english,
                    "type": "grammar",
                    "category": "grammar_word_classes",
                    "notes": notes,
                }
            )

    question_words = data.get("question_words", {})
    for entry in question_words.get("entries", []):
        if entry.get("needs_review"):
            continue
        luganda = entry.get("luganda")
        english = entry.get("english")
        if not luganda or not english:
            continue
        rows.append(
            {
                "luganda": luganda,
                "english": english,
                "type": "grammar",
                "category": "grammar_question_words",
                "notes": entry.get("example"),
            }
        )
    return rows
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_export_full_dataset.py -v -k word_classes`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/export_full_dataset.py tests/test_export_full_dataset.py
git commit -m "feat: word_classes extractor for full dataset export"
```

---

### Task 6: Dispatcher, file discovery, and export() orchestration with summary + dry-run

**Files:**
- Modify: `scripts/export_full_dataset.py`
- Test: `tests/test_export_full_dataset.py`

Wire all five extractors together: walk the four `datasets/` subdirectories, dispatch each file to the right extractor by directory name (vocabulary/sentences → `extract_vocabulary_or_sentence_entries`; proverbs → `extract_proverb_entries`; grammar files dispatch further by filename: `consonants.json`/`vowels.json` → `extract_grammar_rules_entries`, `verb_tenses.json` → `extract_verb_tenses_entries`, `word_classes.json` → `extract_word_classes_entries`), collect all rows, print a per-type and per-category count summary, and write the JSONL (or skip writing on `--dry-run`).

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_export_full_dataset.py
import json
import tempfile
from pathlib import Path

from scripts.export_full_dataset import build_dataset, write_export


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_export_full_dataset.py -v -k "build_dataset or write_export"`
Expected: FAIL with `ImportError: cannot import name 'build_dataset'`

- [ ] **Step 3: Write minimal implementation**

Replace the placeholder `main()` in `scripts/export_full_dataset.py` and add the orchestration functions:

```python
def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_dataset(datasets_dir: Path) -> list[dict]:
    """Walk datasets_dir's vocabulary/sentences/grammar/proverbs subdirs and extract all rows."""
    rows: list[dict] = []

    vocabulary_dir = datasets_dir / "vocabulary"
    if vocabulary_dir.exists():
        for path in sorted(vocabulary_dir.glob("*.json")):
            rows.extend(extract_vocabulary_or_sentence_entries(_load_json(path), row_type="vocabulary"))

    sentences_dir = datasets_dir / "sentences"
    if sentences_dir.exists():
        for path in sorted(sentences_dir.glob("*.json")):
            rows.extend(extract_vocabulary_or_sentence_entries(_load_json(path), row_type="sentence"))

    proverbs_dir = datasets_dir / "proverbs"
    if proverbs_dir.exists():
        for path in sorted(proverbs_dir.glob("*.json")):
            rows.extend(extract_proverb_entries(_load_json(path)))

    grammar_dir = datasets_dir / "grammar"
    if grammar_dir.exists():
        grammar_dispatch = {
            "consonants.json": extract_grammar_rules_entries,
            "vowels.json": extract_grammar_rules_entries,
            "verb_tenses.json": extract_verb_tenses_entries,
            "word_classes.json": extract_word_classes_entries,
        }
        for path in sorted(grammar_dir.glob("*.json")):
            extractor = grammar_dispatch.get(path.name)
            if extractor is None:
                logger.warning(f"No grammar extractor registered for {path.name}, skipping")
                continue
            rows.extend(extractor(_load_json(path)))

    return rows


def write_export(rows: list[dict], output_dir: Path, today: str | None = None) -> Path:
    """Write rows to output_dir/full_dataset_export_<today>.jsonl. today defaults to date.today()."""
    today = today or date.today().isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"full_dataset_export_{today}.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return output_path


def print_summary(rows: list[dict]) -> None:
    by_type: dict[str, int] = {}
    by_category: dict[str, int] = {}
    for row in rows:
        by_type[row["type"]] = by_type.get(row["type"], 0) + 1
        by_category[row["category"]] = by_category.get(row["category"], 0) + 1

    print("\nFull Dataset Export Summary")
    print("-" * 40)
    print(f"  Total rows: {len(rows)}")
    print("\n  By type:")
    for t, count in sorted(by_type.items()):
        print(f"    {t:12s} {count}")
    print("\n  By category:")
    for c, count in sorted(by_category.items()):
        print(f"    {c:25s} {count}")


def main():
    parser = argparse.ArgumentParser(description="Export full vocabulary/sentence/grammar/proverb dataset")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    rows = build_dataset(DATASETS_DIR)
    print_summary(rows)

    if args.dry_run:
        print("\n  [DRY RUN] No file written.")
        return

    output_path = write_export(rows, OUTPUT_DIR)
    print(f"\n  Output: {output_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_export_full_dataset.py -v`
Expected: PASS (all tests across Tasks 1-6, 13 total)

- [ ] **Step 5: Commit**

```bash
git add scripts/export_full_dataset.py tests/test_export_full_dataset.py
git commit -m "feat: orchestrate full dataset export with dry-run and summary"
```

---

### Task 7: Run the real export and sanity-check counts

**Files:** None created — this is a manual verification step against the real `datasets/` tree.

- [ ] **Step 1: Run dry-run against the real dataset**

Run: `python scripts/export_full_dataset.py --dry-run`

Expected output: a summary block with `Total rows`, a `By type` breakdown showing `vocabulary`, `sentence`, `grammar`, `proverb` counts, and a `By category` breakdown. Sanity-check: `vocabulary` should be in the low-400s (12 files, ~424 entries per existing memory notes, minus any `needs_review: true` skips), `sentence` should be around 100-110, `proverb` around 60, `grammar` will be much smaller than those (one row per rule for consonants/vowels, plus flattened tense/word-class examples — expect roughly 30-60 total, not in the hundreds, since rules[] files now yield 1 row per rule rather than per example).

- [ ] **Step 2: Run the real export (writes the file)**

Run: `python scripts/export_full_dataset.py`

Expected: `data/training/full_dataset_export_2026-06-23.jsonl` created (filename uses today's actual date).

- [ ] **Step 3: Manually inspect a sample**

Run: `python -c "import json; lines = open('data/training/full_dataset_export_2026-06-23.jsonl', encoding='utf-8').readlines(); [print(json.loads(l)) for l in lines[:5]]; [print(json.loads(l)) for l in lines[-5:]]"`

Expected: first 5 rows look like valid vocabulary rows (luganda/english pairs make sense), last 5 rows look like valid grammar rows. No `null` for `luganda` or `english` in any row.

- [ ] **Step 4: Commit the export output**

```bash
git add data/training/full_dataset_export_*.jsonl
git commit -m "data: full dataset export for HuggingFace upload"
```

---

### Task 8: Upload script

**Files:**
- Create: `scripts/upload_full_dataset_to_huggingface.py`

Mirrors `scripts/upload_to_huggingface.py`'s structure (load latest export → build `Dataset` → `push_to_hub` → upload a dataset card), but loads `full_dataset_export_*.jsonl` instead, defaults `--repo` to `MukalaziPatrick/luganda-vocabulary-dataset`, and uses a dataset card describing this as the curated corpus (not corrections).

- [ ] **Step 1: Write the script**

```python
# scripts/upload_full_dataset_to_huggingface.py

"""
Upload the curated Luganda vocabulary/sentence/grammar/proverb dataset to
HuggingFace Hub. This is the full corpus that powers search/translate in
Luganda AI Studio — distinct from scripts/upload_to_huggingface.py, which
uploads user-submitted correction pairs (a separate, much smaller dataset).

REQUIREMENTS:
  pip install huggingface_hub datasets

SETUP (one-time):
  hf auth login
  -- OR --
  Set environment variable: HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx

USAGE:
  python scripts/upload_full_dataset_to_huggingface.py --dry-run
  python scripts/upload_full_dataset_to_huggingface.py --repo MukalaziPatrick/luganda-vocabulary-dataset

WHAT GETS UPLOADED:
  The most recent data/training/full_dataset_export_*.jsonl file.

DATASET SCHEMA:
  Each row:
    luganda   str         — Luganda text
    english   str         — English text
    type      str         — "vocabulary" | "sentence" | "grammar" | "proverb"
    category  str         — source category (e.g. "animals", "grammar_verb_tenses")
    notes     str | null  — additional context (meaning, theme, rule explanation)
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

EXPORT_DIR = PROJECT_ROOT / "data" / "training"

DATASET_CARD = """\
---
language:
- lug
- en
license: cc-by-4.0
task_categories:
- translation
- text-classification
tags:
- luganda
- english
- low-resource
- vocabulary
- grammar
pretty_name: Luganda-English Vocabulary, Sentence, Grammar, and Proverb Corpus
size_categories:
- n<1K
---

# Luganda ↔ English Vocabulary/Sentence/Grammar/Proverb Dataset

The curated corpus powering search and translation in
[Luganda AI Studio](https://github.com/MukalaziPatrick/luganda-ai-studio) —
vocabulary, example sentences, grammar rules, and traditional proverbs, each
human-verified by a native Luganda speaker.

## Dataset Description

Unlike the companion `luganda-en-dataset` (user-submitted correction pairs),
this dataset is the original curated reference corpus: dictionary-style
vocabulary entries, everyday sentence pairs, grammar rule explanations, and
Kiganda proverbs with their meanings.

## Schema

| Column | Type | Description |
|---|---|---|
| luganda | string | Luganda text |
| english | string | English text |
| type | string | `vocabulary`, `sentence`, `grammar`, or `proverb` |
| category | string | Source category, e.g. `animals`, `grammar_verb_tenses` |
| notes | string or null | Additional context: word meaning, proverb theme, or grammar rule explanation |

## Usage

```python
from datasets import load_dataset

ds = load_dataset("MukalaziPatrick/luganda-vocabulary-dataset")
```

## License

CC BY 4.0 — Free to use with attribution.
"""


def _load_latest_export() -> list[dict]:
    """Load the most recent full_dataset_export_*.jsonl file."""
    exports = sorted(EXPORT_DIR.glob("full_dataset_export_*.jsonl"))
    if not exports:
        logger.error("No full_dataset_export_*.jsonl found. Run scripts/export_full_dataset.py first.")
        sys.exit(1)
    path = exports[-1]
    logger.info(f"Loading: {path.name}")
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    logger.info(f"Rows to upload: {len(records)}")
    return records


def _upload(records: list[dict], repo_id: str, private: bool, token: str) -> None:
    """Upload records to HuggingFace Hub as a dataset."""
    try:
        from datasets import Dataset
        from huggingface_hub import HfApi
    except ImportError:
        logger.error(
            "Missing dependencies.\n"
            "Install with: pip install huggingface_hub datasets"
        )
        sys.exit(1)

    api = HfApi(token=token)

    logger.info(f"Creating/verifying dataset repo: {repo_id}")
    api.create_repo(
        repo_id=repo_id,
        repo_type="dataset",
        private=private,
        exist_ok=True,
    )

    ds = Dataset.from_list(records)
    logger.info(f"Dataset built: {ds}")

    logger.info(f"Pushing to Hub: {repo_id} ...")
    ds.push_to_hub(repo_id, token=token, private=private)
    logger.info(f"Dataset pushed successfully: https://huggingface.co/datasets/{repo_id}")

    card_path = EXPORT_DIR / "FULL_DATASET_README.md"
    card_path.write_text(
        DATASET_CARD.replace("MukalaziPatrick/luganda-vocabulary-dataset", repo_id), encoding="utf-8"
    )
    api.upload_file(
        path_or_fileobj=str(card_path),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="dataset",
        token=token,
    )
    logger.info("Dataset card uploaded.")
    logger.info(f"\nDone! View at: https://huggingface.co/datasets/{repo_id}")


def main():
    parser = argparse.ArgumentParser(description="Upload full Luganda dataset to HuggingFace Hub")
    parser.add_argument(
        "--repo",
        default="MukalaziPatrick/luganda-vocabulary-dataset",
        help="HuggingFace dataset repo ID",
    )
    parser.add_argument("--private", action="store_true", help="Create as private repo")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be uploaded, do not upload")
    args = parser.parse_args()

    records = _load_latest_export()

    if args.dry_run:
        logger.info("[DRY RUN] Would upload:")
        for i, r in enumerate(records[:5], 1):
            logger.info(f"  {i}. [{r['type']}] {r['luganda']!r} -> {r['english']!r}")
        if len(records) > 5:
            logger.info(f"  ... and {len(records) - 5} more")
        logger.info("[DRY RUN] No upload performed.")
        return

    token = os.getenv("HF_TOKEN", "")
    if not token:
        try:
            from huggingface_hub import HfFolder
            token = HfFolder.get_token() or ""
        except Exception:
            pass

    if not token:
        logger.error(
            "No HuggingFace token found.\n"
            "Run: hf auth login\n"
            "OR:  set HF_TOKEN=hf_xxxx in your environment"
        )
        sys.exit(1)

    _upload(records, args.repo, args.private, token)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Dry-run to verify it loads the export correctly**

Run: `python scripts/upload_full_dataset_to_huggingface.py --dry-run`
Expected: logs `Rows to upload: <N>` matching Task 7's total, then prints 5 sample rows in `[type] 'luganda' -> 'english'` format, ends with `[DRY RUN] No upload performed.`

- [ ] **Step 3: Commit**

```bash
git add scripts/upload_full_dataset_to_huggingface.py
git commit -m "feat: upload script for full vocabulary/sentence/grammar/proverb dataset"
```

---

### Task 9: Real upload to HuggingFace and verification

**Files:** None created — this is the live upload + manual verification step.

- [ ] **Step 1: Run the real upload**

Run: `python scripts/upload_full_dataset_to_huggingface.py --repo MukalaziPatrick/luganda-vocabulary-dataset`
Expected: logs ending in `Done! View at: https://huggingface.co/datasets/MukalaziPatrick/luganda-vocabulary-dataset`

- [ ] **Step 2: Verify live on HuggingFace**

Open `https://huggingface.co/datasets/MukalaziPatrick/luganda-vocabulary-dataset` in a browser. Confirm: dataset card renders (title "Luganda ↔ English Vocabulary/Sentence/Grammar/Proverb Dataset"), row count in the dataset viewer matches Task 7's total, and the four `type` values (vocabulary/sentence/grammar/proverb) are all present when browsing sample rows.

- [ ] **Step 3: Commit the README artifact left in the repo**

```bash
git add data/training/FULL_DATASET_README.md
git commit -m "docs: dataset card for full vocabulary/sentence/grammar/proverb HF upload"
```

---

## Plan self-review notes

- **Spec coverage:** vocabulary/sentence (Task 1), proverb (Task 2), grammar rules[] one-row-per-rule (Task 3), verb_tenses (Task 4), word_classes+question_words (Task 5), orchestration+dry-run+summary (Task 6), real export (Task 7), upload script (Task 8), real upload+verification (Task 9). All spec sections covered.
- **Out of scope confirmed untouched:** no task modifies `scripts/export_dataset.py` or `scripts/upload_to_huggingface.py`.
- **Type consistency:** all extractor functions return `{"luganda", "english", "type", "category", "notes"}` dicts; `build_dataset` and `write_export` consume that exact shape; `upload_full_dataset_to_huggingface.py`'s dry-run print uses `r["type"]`/`r["luganda"]`/`r["english"]` matching the same schema.
