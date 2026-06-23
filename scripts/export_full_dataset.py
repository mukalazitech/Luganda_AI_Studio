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
