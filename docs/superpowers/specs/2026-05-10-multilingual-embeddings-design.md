# Multilingual Embeddings Upgrade — Design Spec
**Date:** 2026-05-10  
**Status:** Approved

---

## Overview

Upgrade the embedding model from `all-MiniLM-L6-v2` (English-optimised, ~90 MB) to `paraphrase-multilingual-MiniLM-L12-v2` (multilingual, ~470 MB). Both produce 384-dimensional vectors, but the new model handles Luganda text significantly better due to multilingual training data.

Brief downtime accepted: stop server → wipe collections → re-ingest → restart.

---

## Architecture

Five files change, one new script added. No new modules, no config changes, no frontend changes.

| File | Action | Change |
|---|---|---|
| `backend/services/ingestion/embedder.py` | MODIFY | Swap model name; add `get_chroma_embedding_fn()` |
| `backend/services/ingestion/indexer.py` | MODIFY | Pass embedding function to `get_or_create_collection` |
| `backend/services/search_service.py` | MODIFY | Pass embedding function to `get_or_create_collection` in query path |
| `backend/services/translation/service.py` | NO CHANGE | Uses `get_embedding_model()` — picks up new model automatically |
| `scripts/reembed.py` | CREATE | Migration script: wipe 4 collections + re-run ingestion |

---

## The Embedding Function

Add to `backend/services/ingestion/embedder.py`:

```python
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

def get_chroma_embedding_fn() -> SentenceTransformerEmbeddingFunction:
    """
    Return a ChromaDB-compatible embedding function using the multilingual model.
    Pass this to get_or_create_collection() and query() so ChromaDB uses
    the same model for both ingestion and search — no mismatch possible.
    """
    return SentenceTransformerEmbeddingFunction(model_name=_MODEL_NAME)
```

**Both ingestion and search use this same function.** ChromaDB caches the model internally, so it is only loaded once per process regardless of how many times `get_chroma_embedding_fn()` is called.

The existing `get_model()`, `get_embedding_model()`, and `embed_texts()` functions remain unchanged. They reference `_model_name` (module-level) so they automatically use the new model after the rename. `translation/service.py` uses these and requires no changes.

---

## Changes to `indexer.py`

Import and pass the embedding function when getting or creating a collection:

```python
from backend.services.ingestion.embedder import get_chroma_embedding_fn

# In index_records(), replace:
collection = client.get_or_create_collection(
    name=collection_name,
    metadata={"description": ..., "hnsw:space": "cosine"}
)

# With:
collection = client.get_or_create_collection(
    name=collection_name,
    embedding_function=get_chroma_embedding_fn(),
    metadata={"description": ..., "hnsw:space": "cosine"}
)
```

Same change applies in `clear_collection()` where it recreates the collection after deletion.

---

## Changes to `search_service.py`

Import and pass the embedding function when accessing each collection for query:

```python
from backend.services.ingestion.embedder import get_chroma_embedding_fn

# In search_knowledge(), replace:
collection = client.get_or_create_collection(col_name)

# With:
collection = client.get_or_create_collection(
    col_name,
    embedding_function=get_chroma_embedding_fn()
)
```

---

## `scripts/reembed.py` — Migration Script

Standalone script, run once with the server stopped.

**Steps executed in order:**

1. **Port check** — warn if port 8000 is in use (server may still be running)
2. **Delete collections** — for each of `vocabulary`, `sentences`, `grammar`, `proverbs`: delete from ChromaDB, confirm deletion. Abort on any failure before proceeding to ingestion.
3. **Re-ingest** — call existing `loader.py` + `indexer.py` pipeline to reload all data from `datasets/` with the new embedding model
4. **Print summary** — final record counts per collection

**Run:**
```bash
python scripts/reembed.py
```

**Expected runtime:** 5–15 minutes on i7-11800H (model download ~470 MB on first run, embedding ~2,500 records in batches of 100).

**Recovery:** If re-ingestion fails mid-way, collections are already wiped. Simply re-run the script — ingestion is idempotent (upsert by stable ID).

---

## Error Handling

- Script aborts before re-ingesting if any collection deletion fails — no partial state where some collections use the new model and some use the old
- ChromaDB embedding function errors surface immediately on first query rather than silently degrading
- Translation pipeline is unaffected during migration (server is stopped)

---

## Testing

No new tests added — the embedding model swap is infrastructure, not new behaviour.

**After migration:**
1. `pytest tests/ -v` — all 11 tests must pass (admin endpoint counts, OpenRouter tracking)
2. Start server, open `http://127.0.0.1:8000/app/search.html` — search "ssebo", expect vocabulary result
3. Open `http://127.0.0.1:8000/app/translate.html` — translate "good morning", expect result through pipeline
4. Check admin dashboard — collection counts should match pre-migration counts

---

## Out of Scope

- Zero-downtime migration (brief downtime accepted)
- Config-driven model name (one-time upgrade, not needed)
- Benchmarking old vs new model quality (accepted on trust)
- Changes to the translation pipeline logic
- Frontend changes
