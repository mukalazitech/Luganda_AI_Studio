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
  python scripts/upload_full_dataset_to_huggingface.py --repo Mukalazipatrick/luganda-vocabulary-dataset

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

ds = load_dataset("Mukalazipatrick/luganda-vocabulary-dataset")
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
    # The repo's own datasets/ directory (source JSON tree) shadows the pip
    # "datasets" package whenever the script runs from the project root, since
    # Python puts the current working directory first on sys.path. Strip CWD
    # entries before importing so the real library resolves.
    original_path = list(sys.path)
    sys.path = [p for p in sys.path if p not in ("", str(PROJECT_ROOT))]
    try:
        from datasets import Dataset
        from huggingface_hub import HfApi
    except ImportError:
        logger.error(
            "Missing dependencies.\n"
            "Install with: pip install huggingface_hub datasets"
        )
        sys.exit(1)
    finally:
        sys.path = original_path

    api = HfApi(token=token)

    logger.info(f"Verifying dataset repo exists: {repo_id}")
    try:
        api.repo_info(repo_id=repo_id, repo_type="dataset")
    except Exception:
        logger.error(
            f"Repo {repo_id} doesn't exist yet. Create it manually at "
            f"https://huggingface.co/new-dataset (API repo creation is blocked for this account), "
            f"then re-run this script."
        )
        sys.exit(1)

    ds = Dataset.from_list(records)
    logger.info(f"Dataset built: {ds}")

    logger.info(f"Pushing to Hub: {repo_id} ...")
    ds.push_to_hub(repo_id, token=token, private=private)
    logger.info(f"Dataset pushed successfully: https://huggingface.co/datasets/{repo_id}")

    card_path = EXPORT_DIR / "FULL_DATASET_README.md"
    card_path.write_text(
        DATASET_CARD.replace("Mukalazipatrick/luganda-vocabulary-dataset", repo_id), encoding="utf-8"
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
        default="Mukalazipatrick/luganda-vocabulary-dataset",
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
            from huggingface_hub import get_token
            token = get_token() or ""
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
