# Multilingual Embeddings Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the ChromaDB embedding model from `all-MiniLM-L6-v2` (English-only) to `paraphrase-multilingual-MiniLM-L12-v2` (multilingual, better Luganda support), unifying both ingestion and search on the same model.

**Architecture:** Add `get_chroma_embedding_fn()` to `embedder.py` returning a `SentenceTransformerEmbeddingFunction`; pass it to every ChromaDB `get_or_create_collection` call in `indexer.py` and `search_service.py`; write a `scripts/reembed.py` migration script that wipes all 4 collections and re-ingests from source JSON files.

**Tech Stack:** Python 3.10+, ChromaDB 1.5.5, sentence-transformers, FastAPI

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `backend/services/ingestion/embedder.py` | MODIFY | Swap model name; add `get_chroma_embedding_fn()` |
| `backend/services/ingestion/indexer.py` | MODIFY | Pass `embedding_function=` to both `get_or_create_collection` calls |
| `backend/services/search_service.py` | MODIFY | Pass `embedding_function=` to `get_or_create_collection` in query loop |
| `scripts/reembed.py` | CREATE | Migration: port check → delete 4 collections → re-ingest |
| `tests/test_embedder.py` | CREATE | Verify `get_chroma_embedding_fn()` returns correct type and model |

---

### Task 1: Update `embedder.py` — swap model, add embedding function

**Files:**
- Modify: `backend/services/ingestion/embedder.py`
- Create: `tests/test_embedder.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_embedder.py`:

```python
from backend.services.ingestion.embedder import get_chroma_embedding_fn


def test_get_chroma_embedding_fn_returns_correct_type():
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    fn = get_chroma_embedding_fn()
    assert isinstance(fn, SentenceTransformerEmbeddingFunction)


def test_get_chroma_embedding_fn_uses_multilingual_model():
    fn = get_chroma_embedding_fn()
    # SentenceTransformerEmbeddingFunction stores model_name as an attribute
    assert fn._model_name == "paraphrase-multilingual-MiniLM-L12-v2"


def test_model_name_constant_is_updated():
    import backend.services.ingestion.embedder as emb
    assert emb._model_name == "paraphrase-multilingual-MiniLM-L12-v2"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd D:\projects\Luganda_AI_Studio
pytest tests/test_embedder.py -v
```

Expected: FAIL — `ImportError: cannot import name 'get_chroma_embedding_fn'`

- [ ] **Step 3: Update `backend/services/ingestion/embedder.py`**

Replace the entire file:

```python
# backend/services/ingestion/embedder.py

"""
Embedder
=========

Wraps the sentence-transformers model to generate text embeddings.

Model used:
  paraphrase-multilingual-MiniLM-L12-v2

Why this model?
  - Multilingual: trained on 50+ languages, handles Luganda far better than
    the English-only all-MiniLM-L6-v2 it replaced
  - Same 384-dimensional output — drop-in replacement
  - ~470 MB (vs ~90 MB for the old model) — acceptable for this hardware
  - Runs on CPU (no VRAM required)
  - ChromaDB supports it via SentenceTransformerEmbeddingFunction

IMPORTANT — two public names for the same model loader:

  get_model()            — used by the ingestion pipeline
  get_embedding_model()  — used by translation/service.py (kept for compatibility)

Both return the same loaded SentenceTransformer object.
Do not remove either — both are actively used.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

_model_name = "paraphrase-multilingual-MiniLM-L12-v2"

# The model is loaded lazily (only when first needed)
_model = None


def get_chroma_embedding_fn():
    """
    Return a ChromaDB-compatible embedding function using the multilingual model.

    Pass this to get_or_create_collection() and query() so ChromaDB uses
    the same model for both ingestion and search — no mismatch possible.

    ChromaDB caches the underlying model internally so it is only loaded
    once per process regardless of how many times this function is called.
    """
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    return SentenceTransformerEmbeddingFunction(model_name=_model_name)


def get_model():
    """
    Load and return the sentence-transformers model.
    Uses lazy loading — model is only downloaded/loaded once.

    First call: downloads ~470MB model (if not cached) and loads it.
    Subsequent calls: returns the already-loaded model instantly.
    """
    global _model

    if _model is not None:
        return _model

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise ImportError(
            "sentence-transformers is not installed.\n"
            "Install it with: pip install sentence-transformers"
        )

    logger.info(f"Loading embedding model: {_model_name}")
    logger.info("(This may take a moment the first time — model will be cached)")

    _model = SentenceTransformer(_model_name)
    logger.info("Embedding model loaded successfully.")
    return _model


def get_embedding_model():
    """
    Alias for get_model().

    This name is used by backend/services/translation/service.py.
    Kept here so that file does not need to be changed.
    """
    return get_model()


def embed_texts(texts: list[str], batch_size: int = 64) -> list[list[float]]:
    """
    Generate embeddings for a list of text strings.

    Parameters
    ----------
    texts : list of str
        The texts to embed. Each text becomes one 384-dim vector.
    batch_size : int
        How many texts to embed at once. Default 64 is safe for 16GB RAM.

    Returns
    -------
    list of list of float
        One embedding vector per input text.
    """
    if not texts:
        return []

    model = get_model()

    logger.info(f"Embedding {len(texts)} texts in batches of {batch_size}...")

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
    )

    logger.info(f"Embedding complete. Shape: {embeddings.shape}")

    return embeddings.tolist()


def embed_single(text: str) -> list[float]:
    """
    Embed a single text string.
    Convenience wrapper around embed_texts.
    """
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text.")

    results = embed_texts([text])
    return results[0]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_embedder.py -v
```

Expected: 3 passed

- [ ] **Step 5: Run full test suite to confirm no regressions**

```bash
pytest tests/ -v
```

Expected: 14 passed (11 existing + 3 new)

- [ ] **Step 6: Commit**

```bash
git add backend/services/ingestion/embedder.py tests/test_embedder.py
git commit -m "feat: upgrade to paraphrase-multilingual-MiniLM-L12-v2, add get_chroma_embedding_fn"
```

---

### Task 2: Update `indexer.py` — pass embedding function to collection calls

**Files:**
- Modify: `backend/services/ingestion/indexer.py`

There are two `get_or_create_collection` call sites: one in `index_records()` and one in `clear_collection()`. Both need the embedding function.

- [ ] **Step 1: Update `backend/services/ingestion/indexer.py`**

Add the import at the top of the file (after the existing imports):

```python
from backend.services.ingestion.embedder import get_chroma_embedding_fn
```

In `index_records()`, find this block (around line 130):

```python
        try:
            collection = client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "description": COLLECTION_DESCRIPTIONS.get(collection_name, ""),
                    "hnsw:space":  "cosine",
                }
            )
```

Replace with:

```python
        try:
            collection = client.get_or_create_collection(
                name=collection_name,
                embedding_function=get_chroma_embedding_fn(),
                metadata={
                    "description": COLLECTION_DESCRIPTIONS.get(collection_name, ""),
                    "hnsw:space":  "cosine",
                }
            )
```

In `clear_collection()`, find this block (around line 237):

```python
        client.get_or_create_collection(
            name=collection_name,
            metadata={
                "description": COLLECTION_DESCRIPTIONS.get(collection_name, ""),
                "hnsw:space":  "cosine",
            }
        )
```

Replace with:

```python
        client.get_or_create_collection(
            name=collection_name,
            embedding_function=get_chroma_embedding_fn(),
            metadata={
                "description": COLLECTION_DESCRIPTIONS.get(collection_name, ""),
                "hnsw:space":  "cosine",
            }
        )
```

- [ ] **Step 2: Run full test suite**

```bash
pytest tests/ -v
```

Expected: 14 passed — no regressions

- [ ] **Step 3: Commit**

```bash
git add backend/services/ingestion/indexer.py
git commit -m "feat: pass multilingual embedding function to indexer collection calls"
```

---

### Task 3: Update `search_service.py` — pass embedding function to query

**Files:**
- Modify: `backend/services/search_service.py`

The `search_knowledge()` function calls `get_or_create_collection(col_name)` in a loop over collections. This call needs the embedding function so ChromaDB uses the same model for query embedding as was used during ingestion.

- [ ] **Step 1: Update `backend/services/search_service.py`**

Add the import after the existing imports at the top:

```python
from backend.services.ingestion.embedder import get_chroma_embedding_fn
```

In `search_knowledge()`, find this block (around line 219):

```python
        try:
            collection = client.get_or_create_collection(col_name)
        except Exception as e:
            logger.warning(f"Could not access collection '{col_name}': {e}")
            continue
```

Replace with:

```python
        try:
            collection = client.get_or_create_collection(
                col_name,
                embedding_function=get_chroma_embedding_fn(),
            )
        except Exception as e:
            logger.warning(f"Could not access collection '{col_name}': {e}")
            continue
```

- [ ] **Step 2: Run full test suite**

```bash
pytest tests/ -v
```

Expected: 14 passed

- [ ] **Step 3: Commit**

```bash
git add backend/services/search_service.py
git commit -m "feat: pass multilingual embedding function to search service"
```

---

### Task 4: Create `scripts/reembed.py` — migration script

**Files:**
- Create: `scripts/reembed.py`

- [ ] **Step 1: Create `scripts/reembed.py`**

```python
# scripts/reembed.py

"""
Re-embed Migration Script
==========================

Wipes all ChromaDB collections and re-ingests from source JSON files
using the new paraphrase-multilingual-MiniLM-L12-v2 embedding model.

BEFORE RUNNING:
  1. Stop the FastAPI server (Ctrl+C in the terminal running uvicorn)
  2. From the project root, run:

       python scripts/reembed.py

EXPECTED RUNTIME:
  5-15 minutes on i7-11800H
  (~470 MB model download on first run, then embedding ~2,500 records)

SAFE TO RE-RUN:
  If it fails mid-way, just run it again. Ingestion is idempotent.
"""

import sys
import socket
import logging
import time
from pathlib import Path

# ── Ensure project root is on path ───────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.db.chroma_client import get_chroma_client
from backend.services.ingestion.loader import load_all_datasets
from backend.services.ingestion.indexer import index_records

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

COLLECTIONS = ["vocabulary", "sentences", "grammar", "proverbs"]


def _port_in_use(port: int) -> bool:
    """Return True if something is listening on the given port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def _check_server_stopped() -> None:
    """Warn if the FastAPI server appears to still be running."""
    if _port_in_use(8000):
        print("\n⚠️  WARNING: Something is running on port 8000.")
        print("   Stop the FastAPI server before re-embedding to avoid conflicts.")
        print("   Press Ctrl+C to abort, or Enter to continue anyway.")
        try:
            input()
        except KeyboardInterrupt:
            print("\nAborted.")
            sys.exit(0)


def _delete_collections(client) -> None:
    """Delete all 4 collections from ChromaDB. Abort on any failure."""
    print("\n🗑️  Deleting existing collections...")
    for name in COLLECTIONS:
        try:
            client.delete_collection(name)
            print(f"   ✅ Deleted: {name}")
        except Exception as e:
            # Collection may not exist yet — that's fine
            print(f"   ℹ️  {name}: {e} (skipping — may not exist)")


def _reindex(client) -> dict:
    """Load all JSON datasets and index into ChromaDB with new embeddings."""
    print("\n📂 Loading data from datasets/...")
    all_records = load_all_datasets()

    for col_name, records in all_records.items():
        status = f"{len(records)} records" if records else "⚠️  0 records"
        print(f"   • {col_name:<12}: {status}")

    total = sum(len(v) for v in all_records.values())
    if total == 0:
        print("\n⚠️  No records loaded. Check datasets/ folder.")
        sys.exit(1)

    print(f"\n🔄 Embedding and indexing {total} records...")
    print("   (First run downloads ~470 MB model — subsequent runs are faster)")

    return index_records(all_records)


def _print_summary(summary: dict, elapsed: float) -> None:
    print("\n" + "=" * 60)
    print("  RE-EMBED COMPLETE")
    print("=" * 60)
    print(f"\n   Time taken: {elapsed:.1f}s\n")
    total = 0
    for col_name, count in summary.items():
        icon = "✅" if count > 0 else "⚠️ "
        print(f"   {icon}  {col_name:<12}: {count} records")
        total += count
    print(f"\n   Total: {total} records")
    print("\n   Next steps:")
    print("   1. Start the server: uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload")
    print("   2. Open http://127.0.0.1:8000/app/search.html and test a search")
    print("   3. Run: pytest tests/ -v")
    print("=" * 60 + "\n")


def main():
    print("\n" + "=" * 60)
    print("  LUGANDA AI STUDIO — RE-EMBED MIGRATION")
    print(f"  Model: paraphrase-multilingual-MiniLM-L12-v2")
    print("=" * 60)

    _check_server_stopped()

    client = get_chroma_client()
    start = time.time()

    _delete_collections(client)
    summary = _reindex(client)

    _print_summary(summary, time.time() - start)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify the script is importable (dry syntax check)**

```bash
cd D:\projects\Luganda_AI_Studio
python -c "import scripts.reembed; print('OK')"
```

Expected: `OK` (or a path error — if so, run `python scripts/reembed.py --help` instead to check syntax)

- [ ] **Step 3: Run full test suite to confirm nothing broke**

```bash
pytest tests/ -v
```

Expected: 14 passed

- [ ] **Step 4: Commit**

```bash
git add scripts/reembed.py
git commit -m "feat: add reembed.py migration script for multilingual model upgrade"
```

---

### Task 5: Run the migration

This task has no code — it executes the migration against the live ChromaDB.

- [ ] **Step 1: Stop the FastAPI server**

In the terminal running uvicorn, press `Ctrl+C`. Confirm port 8000 is free:

```bash
curl http://127.0.0.1:8000/api/v1/health/
```

Expected: connection refused (server is stopped)

- [ ] **Step 2: Run the migration script**

```bash
cd D:\projects\Luganda_AI_Studio
python scripts/reembed.py
```

Expected output (abridged):
```
==============================
  LUGANDA AI STUDIO — RE-EMBED MIGRATION
  Model: paraphrase-multilingual-MiniLM-L12-v2
==============================

🗑️  Deleting existing collections...
   ✅ Deleted: vocabulary
   ✅ Deleted: sentences
   ✅ Deleted: grammar
   ✅ Deleted: proverbs

📂 Loading data from datasets/...
   • vocabulary  : NNN records
   • sentences   : NNN records
   • grammar     : NNN records
   • proverbs    : NNN records

🔄 Embedding and indexing NNN records...
   (First run downloads ~470 MB model — subsequent runs are faster)

==============================
  RE-EMBED COMPLETE
==============================
   Time taken: NNN s

   ✅  vocabulary  : NNN records
   ✅  sentences   : NNN records
   ✅  grammar     : NNN records
   ✅  proverbs    : NNN records
```

Wait for completion — first run takes 5–15 minutes for the model download.

- [ ] **Step 3: Restart the server**

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- [ ] **Step 4: Run full test suite**

```bash
pytest tests/ -v
```

Expected: 14 passed

- [ ] **Step 5: Smoke test — search**

Open `http://127.0.0.1:8000/app/search.html` and search for `ssebo`. Expect a vocabulary result with a strong match score.

- [ ] **Step 6: Smoke test — translate**

Open `http://127.0.0.1:8000/app/translate.html` and translate `good morning`. Expect a result (any match type).

- [ ] **Step 7: Smoke test — admin dashboard**

Open `http://127.0.0.1:8000/app/admin.html`. Verify collection counts match what the migration script reported.

- [ ] **Step 8: Commit migration confirmation**

```bash
git add .
git commit -m "chore: run multilingual embedding migration — all collections re-indexed"
```

---

## Self-Review

### Spec coverage

| Spec requirement | Task |
|---|---|
| Swap model name to `paraphrase-multilingual-MiniLM-L12-v2` | Task 1 |
| Add `get_chroma_embedding_fn()` to `embedder.py` | Task 1 |
| Pass embedding function to `indexer.py` collection calls | Task 2 |
| Pass embedding function to `search_service.py` query | Task 3 |
| `translation/service.py` — no change needed | ✅ Confirmed (uses `get_embedding_model()` which picks up new `_model_name`) |
| `scripts/reembed.py` migration script | Task 4 |
| Port check before deletion | Task 4 (`_check_server_stopped`) |
| Delete 4 collections, abort on failure | Task 4 (`_delete_collections`) |
| Re-run ingestion via existing loader + indexer | Task 4 (`_reindex`) |
| Print final counts | Task 4 (`_print_summary`) |
| Run migration | Task 5 |
| Verify with pytest + smoke tests | Task 5 |

### Placeholder scan

No TBDs, TODOs, or vague steps. All code is complete.

### Type consistency

- `get_chroma_embedding_fn()` defined in Task 1, imported in Task 2 and Task 3 — name matches exactly.
- `_model_name` (module-level in `embedder.py`) referenced in `test_model_name_constant_is_updated` — matches the variable name in the implementation.
- `SentenceTransformerEmbeddingFunction._model_name` attribute — this is the internal attribute ChromaDB's embedding function exposes. If this attribute name differs in the installed version, the test `test_get_chroma_embedding_fn_uses_multilingual_model` may need adjustment. Fallback: check `str(fn)` for the model name instead.
