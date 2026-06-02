# Luganda AI Studio — Handoff Report
> Last updated: 2026-05-14 | Session: 7-Task Maintenance Sprint
> Read this at the start of every new session before touching any file.

---

## 1. What This App Is

A local-first AI application for Luganda ↔ English translation, semantic search,
interactive teaching/flashcards, user feedback collection, and AI chat.
Built with FastAPI + ChromaDB + NLLB-200 + Ollama. All AI runs on the user's machine
(RTX 3050, 4 GB VRAM).

**Live URL (permanent):** https://app.lugandastudio.com
_(Tunnel auto-starts with Windows. Only start.bat is needed manually.)_

---

## 2. How to Start the App

**Step 1 — Double-click `start.bat`** in `D:\projects\Luganda_AI_Studio\`

This opens two windows:
- **Luganda API Server** — FastAPI backend on http://127.0.0.1:8000
- **Cloudflare Tunnel** — public HTTPS at https://app.lugandastudio.com

Wait for: `INFO: Application startup complete.`

**Step 2 (optional) — Start Ollama for chat:**
```
ollama serve
```
Without this, chat shows "offline" but translate/search/teach all work.

### Quick verify URLs
| Page | URL |
|---|---|
| Home | http://127.0.0.1:8000/app/index.html |
| Translate | http://127.0.0.1:8000/app/translate.html |
| Admin | http://127.0.0.1:8000/app/admin.html |
| API health | http://127.0.0.1:8000/api/v1/health |

---

## 3. Session 2026-05-14 — What Was Done

### Summary
7 maintenance tasks completed. 149 tests passing. TTS caching live.
LoRA script built. Dataset exported.

---

### Task 1 — Multilingual Embeddings (CONFIRMED ALREADY DONE)
**Status:** Complete from a prior session. No work needed.

`backend/services/ingestion/embedder.py` already uses `paraphrase-multilingual-MiniLM-L12-v2`.
ChromaDB has 4 collections populated with the correct embeddings.
`scripts/reembed.py` exists and is ready to re-run if the dataset changes.

---

### Task 2 — TTS Audio Caching
**File changed:** `backend/services/tts/mms_tts_service.py`

**What changed:**
- Added SHA-256 disk cache at `data/tts_cache/<hash>.wav`
- On first synthesis: model runs, WAV saved to disk
- On repeat requests: WAV served directly from disk (instant, no model call)
- Cache survives server restarts

**How to test:**
1. Start the server
2. Open http://127.0.0.1:8000/app/translate.html
3. Type `Webale`, click 🔊 — first play takes ~10s
4. Click 🔊 again — must be instant
5. Check `data/tts_cache/` — `.wav` files appear there

**Cache location:** `D:\projects\Luganda_AI_Studio\data\tts_cache\`

---

### Task 3 — Test Suite Fixed (133 → 133 passing)
**File changed:** `tests/test_feedback_route.py`

**What changed:**
- Installed pytest (was not installed in the venv)
- Found 1 failing test: `test_missing_provided_translation_returns_422`
- Root cause: test expected 422, but `translated_text` is intentionally `Optional`
  (needed so users can correct `not_found` results where there is no translation to report)
- Fixed: renamed test to `test_missing_provided_translation_is_allowed`, changed assertion to 200
- All 133 tests pass

**Run tests:**
```
cd D:\projects\Luganda_AI_Studio
venv\Scripts\activate
python -m pytest tests/ -v
```

---

### Task 4 — New Tests Added (133 → 149 passing)
**Files created:**
- `tests/test_admin_degradation.py` — 10 tests
- `tests/test_tts_cache.py` — 6 tests

**Admin degradation tests cover:**
- Endpoint always returns 200 even when ChromaDB is down
- `api_status` is always `"ok"`
- Graceful degradation with no TTS deps, no OpenRouter key
- All counts are non-negative integers
- `collections.total` equals sum of individual counts
- `nllb_loaded` is always a boolean

**TTS cache tests cover:**
- Cache path is deterministic for same text
- Different text → different cache path
- Cache filename is SHA-256 of text
- First call writes WAV to disk
- Second call reads from disk without calling model
- Cache miss triggers model call

---

### Task 5 — TTS + STT End-to-End (Manual Test Required)
**No code changed.** This requires a running server and browser.

**TTS test:**
1. Open translate.html → type any Luganda word → click 🔊
2. First call: ~10s (model loads). Repeat: instant.

**STT test:**
1. Click 🎙 → allow mic → speak a word
2. First call: ~20-30s (Whisper downloads ~300 MB)
3. Transcribed text appears in the input box

**Known behaviour:** Whisper hallucinates Luganda phrases on silence — this is normal.

---

### Task 6 — LoRA Fine-tuning Script
**File created:** `scripts/finetune_lora.py`

**What it does:**
- Fine-tunes `facebook/nllb-200-distilled-600M` on verified correction pairs
- Uses LoRA (rank 8) so it fits in 4 GB VRAM via 8-bit quantisation
- Saves adapter only (~10 MB) — not the full model

**Current state:** Only 1 verified pair in the dataset. Need 500 before training.

**Commands:**
```
# Check how many pairs you have
python scripts/finetune_lora.py --check

# Dry-run (loads model, validates data, no training)
python scripts/finetune_lora.py --dry-run

# Train (run only when --check shows 500+)
python scripts/finetune_lora.py

# Force train with fewer pairs (risky — overfitting)
python scripts/finetune_lora.py --force
```

**Install deps first (one-time):**
```
pip install peft accelerate bitsandbytes
```

**Output goes to:** `data/lora/YYYY-MM-DD/adapter_model.bin`

---

### Task 7 — Dataset Export + HuggingFace Upload
**File created:** `scripts/upload_to_huggingface.py`
**Export run:** `data/training/dataset_export_2026-05-14.jsonl` (20 verified pairs)

**To upload to HuggingFace (when ready):**
```
pip install huggingface_hub datasets
huggingface-cli login
python scripts/upload_to_huggingface.py --repo MukalaziPatrick/luganda-en-dataset
```

**Dry-run first:**
```
python scripts/upload_to_huggingface.py --dry-run
```

**Dataset card** is auto-generated and uploaded to the repo with CC BY 4.0 licence.

---

## 4. Current Test Suite State

```
tests/test_admin.py                  7 tests   — admin status structure
tests/test_admin_degradation.py     10 tests   — admin graceful degradation  ← NEW
tests/test_embedder.py               3 tests   — multilingual model check
tests/test_feedback_route.py        31 tests   — feedback POST/GET routes
tests/test_knowledge_routes.py      13 tests   — search + stats routes
tests/test_openrouter_tracking.py    4 tests   — OpenRouter last-call tracking
tests/test_search_service.py         5 tests   — search normalisation helpers
tests/test_stt_route.py              5 tests   — STT route
tests/test_translate_pipeline.py    17 tests   — 5-pass translation pipeline
tests/test_translate_route.py       48 tests   — translate HTTP route
tests/test_tts_cache.py              6 tests   — TTS disk cache             ← NEW
──────────────────────────────────────────────────────────────
TOTAL                              149 tests   ALL PASSING
```

---

## 5. What Still Needs Doing (Next Sessions)

| Priority | Task | Notes |
|---|---|---|
| HIGH | Collect more correction pairs | Need 499 more before LoRA training. Users must submit corrections via the ✗ button. |
| HIGH | Test TTS + STT on mobile | Open https://app.lugandastudio.com on Android, test 🔊 and 🎙 on a phone browser |
| MEDIUM | Upload dataset to HuggingFace | Run `upload_to_huggingface.py` — needs HF account login first |
| MEDIUM | Add more vocabulary data | More source JSON in `datasets/vocabulary/` → run `scripts/reembed.py` |
| LOW | LoRA fine-tuning | Run when 500+ verified correction pairs accumulated |
| LOW | GPU acceleration for NLLB | NLLB runs on CPU (~5-10s). Move to RTX 3050 for ~1s response. Needs `torch` with CUDA build. |

---

## 6. Translation Pipeline — How It Works

```
User input
  → Pass 1: Exact match        (confidence 1.00) — strip whitespace, case preserved
  → Pass 2: Normalized match   (confidence 0.98) — both sides lowercased
  → Pass 3: Partial match      (confidence 0.85) — "stomach" matches "Stomach / Belly"
  → Pass 4: Semantic match     (confidence variable, threshold 0.50) — multilingual MiniLM
  → Pass 5: OpenRouter API     (confidence 0.75) — LLM neural fallback (key already set)
  → Pass 6: NLLB-200 local     (confidence 0.70) — on-device neural fallback
  → not_found                  — if all passes fail
```

**OpenRouter key:** Already set in `.env`. Model: `google/gemma-2-9b-it:free`

---

## 7. Full Data Map

| Data | Path | Notes |
|---|---|---|
| ChromaDB | `data/chromadb/` | 4 collections, multilingual embeddings |
| TTS cache | `data/tts_cache/` | WAV files, SHA-256 named — NEW |
| Feedback log | `data/feedback/feedback_log.jsonl` | All user ratings |
| Corrections | `data/training/corrections.jsonl` | Full correction records |
| Training pairs | `data/training/training_pairs.jsonl` | Minimal format for LoRA |
| Dataset export | `data/training/dataset_export_2026-05-14.jsonl` | 20 verified pairs |
| LoRA output | `data/lora/YYYY-MM-DD/` | Created when fine-tuning runs |

**Data does NOT go to the cloud.** All AI runs locally.

---

## 8. Machine Specs (Never Forget)

| Component | Spec |
|---|---|
| OS | Windows 11, 64-bit |
| CPU | Intel Core i7-11800H |
| RAM | 16 GB |
| GPU | NVIDIA RTX 3050 Laptop |
| VRAM | 4 GB |

**Rule:** No training large models from scratch. NLLB-200-distilled-600M is the ceiling.
All features must work on 4 GB VRAM or CPU fallback.

---

## 9. Tunnel + Domain

| Item | Value |
|---|---|
| Domain | lugandastudio.com (Cloudflare, renews May 2027) |
| Public URL | https://app.lugandastudio.com |
| Tunnel name | luganda-studio |
| Tunnel ID | edcb6439-b31a-4541-bc42-4eaf5c536686 |
| Tunnel config | `C:\Users\patri\.cloudflared\config.yml` |
| Tunnel credentials | `C:\Users\patri\.cloudflared\edcb6439-....json` (keep secret) |
| Windows service | Installed — auto-starts on boot |

---

## 10. Key File Index

| File | Purpose |
|---|---|
| `start.bat` | Start everything — double-click this |
| `backend/main.py` | FastAPI app entry point |
| `backend/services/translation/service.py` | 6-pass translation pipeline |
| `backend/services/tts/mms_tts_service.py` | TTS with disk cache |
| `backend/services/stt/whisper_service.py` | Whisper STT |
| `backend/services/ingestion/embedder.py` | Multilingual MiniLM embeddings |
| `backend/db/chroma_client.py` | ChromaDB singleton |
| `scripts/reembed.py` | Wipe + re-index ChromaDB after model change |
| `scripts/export_dataset.py` | Export verified pairs to JSONL |
| `scripts/finetune_lora.py` | LoRA fine-tuning (run when 500+ pairs) |
| `scripts/upload_to_huggingface.py` | Upload dataset to HF Hub |
| `scripts/process_feedback.py` | Re-process feedback into ChromaDB |
| `CLAUDE.md` | Full project rules — Claude reads this every session |
| `HANDOFF.md` | This file |
