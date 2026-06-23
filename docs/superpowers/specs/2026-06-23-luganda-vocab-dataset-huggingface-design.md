# Luganda vocabulary/sentence/grammar/proverb dataset → HuggingFace

## Why

Roadmap item "dataset expansion toward 622+ records / HuggingFace upload" had been pending
since 2026-05-22 in `project_luganda_app.md`, but the existing `scripts/upload_to_huggingface.py`
only exports **verified user-correction pairs** (currently 25 after dedup), not the curated
622-record vocabulary/sentence/grammar/proverb corpus that actually powers search/translate.
This is a distinct, net-new export+upload covering the real curated dataset.

## Scope

Source data: `datasets/{vocabulary,sentences,grammar,proverbs}/*.json` (12 vocabulary files +
2 sentence files + 4 grammar files + 1 proverbs file). Not the ChromaDB volume, not the
correction-pairs pipeline — those are untouched.

## Output schema (one flat JSONL)

```json
{
  "luganda": "str",
  "english": "str",
  "type": "vocabulary | sentence | grammar | proverb",
  "category": "str (e.g. animals, daily_life, grammar_verb_tenses)",
  "notes": "str | null"
}
```

Rows missing both `luganda` and `english` are skipped. Rows flagged `needs_review: true` in
source data are **excluded** (same data-quality bar as the gloss-audit work already done on
this dataset).

## Per-source-type extraction

- **vocabulary / sentences** (`entries[]` with `luganda`/`english`): direct mapping. `notes`
  from the entry's `note` field if present, else null.
- **proverbs** (`entries[]` with `luganda`/`english`/`theme`/`meaning`): `notes` = `meaning`
  (theme folded into the same notes string, e.g. `"[hardwork] Whatever you plant..."`).
- **grammar** — three distinct internal shapes require separate handling:
  - `rules[]` (consonants.json, vowels.json): for each rule, emit one row per item in the
    rule's `examples[]` (luganda_example/english_meaning, or equivalent key names found per
    file), `notes` = rule's `explanation`, `category` = `grammar_<rule's source category>`.
  - `tenses[]` (verb_tenses.json): for each tense, flatten both `examples[]`
    (`luganda_infinitive` or `everyday_form` → english_everyday) and `sentence_examples[]`
    (`luganda`/`english` directly), `notes` = tense's `description`.
  - `word_classes[]` + `question_words.entries[]` (word_classes.json): flatten each word
    class's `examples[]` (luganda/english), `notes` = class's `description`; question_words
    entries map directly (luganda/english/`example` as notes).
- Any row-producing step where the expected key is missing on a given record is skipped (not
  fatal) — logged as a count in the export summary, mirroring `export_dataset.py`'s style.

## Scripts (two, mirroring existing correction-pairs pattern)

1. `scripts/export_full_dataset.py`
   - `--dry-run` flag prints a summary (per-type and per-category counts, skipped count) without
     writing.
   - Writes `data/training/full_dataset_export_YYYY-MM-DD.jsonl`.
2. `scripts/upload_full_dataset_to_huggingface.py`
   - Loads the most recent `full_dataset_export_*.jsonl`.
   - Writes a dataset card describing this as the curated vocabulary/sentence/grammar/proverb
     corpus (distinct from the correction-pairs dataset card).
   - `--repo` defaults to `MukalaziPatrick/luganda-vocabulary-dataset` (new repo, separate from
     `luganda-en-dataset` to avoid conflating the two datasets).
   - `--private` flag, same convention as the existing upload script.
   - Reuses the already-authenticated `hf` CLI session (confirmed logged in as
     `Mukalazipatrick`) — no new auth setup needed.

## Out of scope

- `scripts/export_dataset.py` / `scripts/upload_to_huggingface.py` (correction-pairs pipeline)
  — untouched, stays pending its own 500-pair trigger per the roadmap's Phase 4.
- ChromaDB volume — not read from; this export goes straight to the source JSON files, which
  are the same files `loader.py` ingests into ChromaDB.
- No changes to the running app, backend, or frontend — this is a standalone offline tooling
  addition.

## Testing

- `--dry-run` on both scripts, inspect printed counts against known totals (e.g. vocabulary
  should land close to 424 entries across the 12 files, sentences ~110, proverbs 60, grammar
  count TBD by flattening).
- Manually inspect a sample of ~10 rows per type in the written JSONL for correctness.
- Real upload to the new HF repo, verify via browser that the dataset card and row count look
  right.
