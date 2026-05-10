# Admin Dashboard — Design Spec
**Date:** 2026-05-10  
**Status:** Approved

---

## Overview

A read-only admin dashboard for monitoring the Luganda AI Studio system. Intended for shared use including non-technical users. No authentication required (local-first app). Accessible at `/app/admin.html`.

---

## Architecture

| Component | Detail |
|---|---|
| Frontend | `frontend/admin.html` — new page, same card style as `reviews.html` |
| Backend | `backend/api/routes/admin.py` — one endpoint: `GET /api/v1/admin/status` |
| Registration | `backend/main.py` — add admin router with prefix `/api/v1/admin` |
| Nav link | `frontend/index.html` — add "Admin" link alongside existing page links |

No new services required. The endpoint aggregates data from:
- ChromaDB client (collection counts, disk usage)
- Config (OpenRouter key presence, daily limit)
- `openrouter_service.py` (last successful call timestamp)
- `data/feedback/feedback_log.jsonl` (feedback stats)
- `data/training/training_pairs.jsonl` + `corrections.jsonl` (training counts)
- `nllb_service.py` (whether model is loaded)
- `transformers` import check (TTS deps installed)

---

## API Response Shape

`GET /api/v1/admin/status`

```json
{
  "system": {
    "api_status": "ok",
    "chroma_connected": true,
    "openrouter_key_set": true,
    "tts_deps_installed": true,
    "chroma_disk_mb": 42.3
  },
  "collections": {
    "vocabulary": 1200,
    "sentences": 800,
    "grammar": 150,
    "proverbs": 90,
    "documents": 12,
    "total": 2252
  },
  "feedback": {
    "total_submissions": 47,
    "last_submission_at": "2026-05-10T14:23:00Z",
    "correct": 30,
    "wrong": 12,
    "needs_review": 5
  },
  "training": {
    "training_pairs": 38,
    "correction_pairs": 44,
    "last_export": "2026-05-10"
  },
  "pipeline": {
    "nllb_loaded": true,
    "openrouter_key_set": true,
    "openrouter_last_call_at": "2026-05-10T14:05:00Z"
  }
}
```

**Notes:**
- `openrouter_last_call_at` is tracked in-memory in `openrouter_service.py`. Set on each successful call, `null` if never called this session. OpenRouter's free tier does not expose spend data via API — daily spend is NOT surfaced in the UI (the in-memory cap in `openrouter_service.py` remains as a safety mechanism only).
- `tts_deps_installed` is detected by attempting `import transformers, scipy` and returning true/false.
- `chroma_disk_mb` is computed from the size of `data/chromadb/` directory.
- `nllb_loaded` reflects whether the NLLB model singleton has been initialised in this server session.

---

## Frontend Layout

Five cards in a 2-column grid:

### Card 1 — System Health
- Status pills (green/red): API responding, ChromaDB connected, OpenRouter key set, TTS deps installed
- Plain text: ChromaDB disk usage in MB

### Card 2 — Collections
- Table: collection name | record count
- Row for each: vocabulary, sentences, grammar, proverbs, documents
- Footer row: **Total**

### Card 3 — Feedback Summary
- Total submissions
- Last submission timestamp
- Breakdown: ✓ Correct | ✗ Wrong | 🔁 Needs Review

### Card 4 — Training Data
- Training pairs count (`training_pairs.jsonl`)
- Correction pairs count (`corrections.jsonl`)
- Last export date (from most recent `dataset_export_*.jsonl` filename)

### Card 5 — Translation Pipeline
- NLLB model loaded: yes/no pill
- OpenRouter key set: yes/no pill
- OpenRouter last successful call: timestamp or "Never"

---

## Files Changed

| File | Action |
|---|---|
| `backend/api/routes/admin.py` | NEW |
| `backend/services/translation/openrouter_service.py` | UPDATE — add `last_call_at` tracking |
| `backend/main.py` | UPDATE — register admin router |
| `frontend/admin.html` | NEW |
| `frontend/index.html` | UPDATE — add Admin nav link |

---

## Error Handling

- If any data source fails (e.g. ChromaDB unreachable, feedback file missing), that section returns nulls/zeros rather than crashing the whole endpoint. Frontend shows "—" for unavailable fields.
- All counts default to 0 if files don't exist yet.

---

## Out of Scope

- Authentication / password gate (local-first app, not needed)
- Ingestion triggers from UI (read-only dashboard)
- Real-time auto-refresh (user refreshes manually)
- OpenRouter spend tracking (not available on free tier via API)
