# scripts/upload_to_huggingface.py

"""
Upload the Luganda AI Studio dataset to HuggingFace Hub.

REQUIREMENTS:
  pip install huggingface_hub datasets

SETUP (one-time):
  huggingface-cli login
  -- OR --
  Set environment variable: HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx

USAGE:
  # Dry-run: show what would be uploaded without actually uploading
  python scripts/upload_to_huggingface.py --dry-run

  # Upload to a new or existing HF dataset repo
  python scripts/upload_to_huggingface.py --repo your-username/luganda-en-dataset

  # Upload as private (default: public)
  python scripts/upload_to_huggingface.py --repo your-username/luganda-en-dataset --private

WHAT GETS UPLOADED:
  The most recent data/training/dataset_export_*.jsonl file.
  Only verified=True pairs are uploaded.

DATASET SCHEMA:
  Each row:
    source      str   — input text
    target      str   — translation
    direction   str   — "en_to_lg" or "lg_to_en"
    verified    bool  — always True (unverified pairs are excluded)
    submitted_at str  — ISO 8601 timestamp
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
task_ids:
- machine-translation
tags:
- luganda
- english
- nllb
- low-resource
pretty_name: Luganda-English Translation Pairs
size_categories:
- n<1K
---

# Luganda ↔ English Translation Dataset

Human-verified Luganda ↔ English translation pairs collected via the
[Luganda AI Studio](https://github.com/MukalaziPatrick/luganda-ai-studio) feedback loop.

## Dataset Description

All pairs in this dataset are **human-verified corrections** submitted by users
who identified incorrect translations and provided the correct output.

## Schema

| Column | Type | Description |
|---|---|---|
| source | string | Input text |
| target | string | Correct translation |
| direction | string | `en_to_lg` or `lg_to_en` |
| verified | bool | Always `True` in this dataset |
| submitted_at | string | ISO 8601 submission timestamp |

## Usage

```python
from datasets import load_dataset

ds = load_dataset("your-username/luganda-en-dataset")
```

## License

CC BY 4.0 — Free to use with attribution.
"""


def _load_latest_export() -> list[dict]:
    """Load the most recent dataset_export_*.jsonl file."""
    exports = sorted(EXPORT_DIR.glob("dataset_export_*.jsonl"))
    if not exports:
        logger.error("No dataset_export_*.jsonl found. Run scripts/export_dataset.py first.")
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
                r = json.loads(line)
                if r.get("verified"):
                    records.append(r)
            except json.JSONDecodeError:
                pass
    logger.info(f"Verified pairs to upload: {len(records)}")
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

    # Create the repo if it does not exist
    logger.info(f"Creating/verifying dataset repo: {repo_id}")
    api.create_repo(
        repo_id=repo_id,
        repo_type="dataset",
        private=private,
        exist_ok=True,
    )

    # Build HuggingFace Dataset
    ds = Dataset.from_list(records)
    logger.info(f"Dataset built: {ds}")

    # Push to Hub
    logger.info(f"Pushing to Hub: {repo_id} ...")
    ds.push_to_hub(repo_id, token=token, private=private)
    logger.info(f"Dataset pushed successfully: https://huggingface.co/datasets/{repo_id}")

    # Upload dataset card
    card_path = EXPORT_DIR / "README.md"
    card_path.write_text(DATASET_CARD.replace("your-username/luganda-en-dataset", repo_id), encoding="utf-8")
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
    parser = argparse.ArgumentParser(description="Upload Luganda dataset to HuggingFace Hub")
    parser.add_argument(
        "--repo",
        default=None,
        help="HuggingFace dataset repo ID, e.g. your-username/luganda-en-dataset",
    )
    parser.add_argument("--private", action="store_true", help="Create as private repo")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be uploaded, do not upload")
    args = parser.parse_args()

    records = _load_latest_export()

    if args.dry_run:
        logger.info("[DRY RUN] Would upload:")
        for i, r in enumerate(records[:5], 1):
            logger.info(f"  {i}. [{r['direction']}] {r['source']!r} → {r['target']!r}")
        if len(records) > 5:
            logger.info(f"  ... and {len(records) - 5} more")
        logger.info("[DRY RUN] No upload performed.")
        return

    if not args.repo:
        logger.error("--repo is required. Example: --repo your-username/luganda-en-dataset")
        sys.exit(1)

    token = os.getenv("HF_TOKEN", "")
    if not token:
        # Try reading from huggingface_hub cache
        try:
            from huggingface_hub import HfFolder
            token = HfFolder.get_token() or ""
        except Exception:
            pass

    if not token:
        logger.error(
            "No HuggingFace token found.\n"
            "Run: huggingface-cli login\n"
            "OR:  set HF_TOKEN=hf_xxxx in your environment"
        )
        sys.exit(1)

    _upload(records, repo_id=args.repo, private=args.private, token=token)


if __name__ == "__main__":
    main()
