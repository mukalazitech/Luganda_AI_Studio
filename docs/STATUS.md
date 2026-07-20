# Luganda AI Studio — Status Archive

> Moved from CLAUDE.md Sections 10 & 11 to keep CLAUDE.md lean.
> Last captured: 2026-05-11 (session C). See ROADMAP_2026-06.md for current direction.

---

## 2026-07 pilot baseline

> Local-only runtime baseline captured 2026-07-20 at 05:29 UTC from `C:\tmp\Luganda_AI_Studio-balanced-pilot`. This is not deployed-state evidence. The server used the canonical `D:\projects\Luganda_AI_Studio\venv\Scripts\python.exe` interpreter (`Python 3.11.9`) and ran without reload on `127.0.0.1:8000`.

### Runtime responses

- Health response from `GET /api/v1/health`: `{"status":"ok","app_name":"Luganda AI Studio","version":"1.0.0","message":"Luganda AI Studio backend is running."}`
- Authoritative Chroma runtime counts from `GET /api/v1/knowledge/status`: `{"collections":{"vocabulary":425,"sentences":2119,"grammar":28,"proverbs":60,"documents":0},"total_documents":2632}`. These are live local Chroma collection counts, not JSON file counts.

| Route | HTTP | Validation |
|---|---:|---|
| `/api/v1/health` | 200 | Valid JSON; 114-character response |
| `/api/v1/knowledge/status` | 200 | Valid JSON; 115-character response |
| `/app/index.html` | 200 | Valid non-empty HTML; 7,596 characters |
| `/app/translate.html` | 200 | Valid non-empty HTML; 49,454 characters |
| `/app/search.html` | 200 | Valid non-empty HTML; 16,634 characters |
| `/app/teach.html` | 200 | Valid non-empty HTML; 30,732 characters |
| `/app/reviews.html` | 200 | Valid non-empty HTML; 14,887 characters |
| `/app/admin.html` | 200 | Valid non-empty HTML; 10,777 characters |
| `/app/chat.html` | 200 | Valid non-empty HTML; 18,247 characters |

### Verification and shutdown

- Frontend `node --test`: 12 tests, 12 passed, 0 failed, 0 cancelled, 0 skipped, 0 todo.
- No backend tests were run for this baseline task.
- The hidden server was stopped immediately after checks. At 05:30 UTC, launcher PID `6040` and uvicorn PID `10468` were both absent, and no process was listening on port `8000`.

## Completed Features (as of 2026-05-11)

| Feature | Notes |
|---|---|
| Phase 1 data scaling | Flores-200 ingested. ChromaDB 492 → 2,500+ pairs |
| NLLB-200 neural fallback | `nllb_service.py` + pipeline Pass 3. Benchmarked 2026-04-19 |
| Feedback loop | Correction UI → API → ChromaDB. Tested 2026-04-19 |
| Feedback API POST | `feedback.py` appends to `feedback_log.jsonl` |
| Data ingestion pipeline | `download_datasets.py`, `ingest_dataset.py`, `process_feedback.py` |
| Quality metrics | Session Summary card live in `translate.html` |
| Feedback review page | `reviews.html` + `GET /api/v1/feedback`. Built 2026-04-19 |
| Teaching mode | `teach.html` full flash card + quiz mode. 5 endpoints. Confirmed 2026-04-19 |
| CSV ingestor | `scripts/ingest_csv.py`. Auto-detect separator, column aliases. Built 2026-04-19 |
| PDF parser | `scripts/ingest_pdf.py`. Table + line pattern modes, direction auto-detect. Built 2026-04-19 |
| OpenRouter API integration | `openrouter_service.py` + pipeline Pass 4.5. Default: gemma-2-9b-it:free. Built 2026-05-10 |
| Luganda TTS (Meta MMS) | `mms_tts_service.py` + `/api/v1/tts`. 🔊 on translate + teach pages. Built 2026-05-10 |
| Dataset export pipeline | `scripts/export_dataset.py`. HuggingFace-compatible, cleaned, versioned. Built 2026-05-10 |
| Admin dashboard | `admin.html` + `GET /api/v1/admin/status`. 5 cards. Built 2026-05-10 |
| Test infrastructure | pytest + 11 tests (admin + openrouter tracking). Built 2026-05-10 |
| Mobile responsive fix | `styles.css` full responsive overhaul. All breakpoints fixed. Built 2026-05-11 |

## Pending (as of 2026-05-11)

| Item | Notes |
|---|---|
| Set OPENROUTER_API_KEY in .env | Required to activate OpenRouter. Free key at openrouter.ai |
| Install TTS deps | `pip install transformers scipy` then test 🔊 button |
| Multilingual embeddings upgrade | Switch MiniLM → paraphrase-multilingual-MiniLM-L12-v2. Requires full re-embed |
| TTS audio caching | Cache common words so teach.html plays instantly after first load |
| Test suite expansion | Add degradation tests for admin; translate pipeline tests |
| LoRA fine-tuning | Only when 500+ correction pairs. Script not yet built |
| Publish dataset to HuggingFace | Run export_dataset.py, create HF dataset repo, upload |

## What Worked (2026-05-11)

- Translation pipeline: exact → normalized → partial → semantic → OpenRouter API → NLLB-200 neural
- Luganda TTS: 🔊 speaker button on translate + teach pages (Meta MMS, real Luganda voice)
- Search across vocabulary, sentences, grammar, proverbs collections
- Feedback collection: users rate translations, corrections auto-ingest into ChromaDB
- Dataset export: produces clean HuggingFace-compatible JSONL
- Reviews page: admin view with stats and filters
- Session quality metrics: live summary on translate page
- Admin dashboard: system health, collection counts, feedback stats, pipeline status
- Test suite: 11 tests passing (`pytest tests/ -v`)
- Mobile responsive layout: all pages work at 360px–768px

## Mobile Responsive Fixes (2026-05-11)

- Removed overly broad `.flex { flex-direction: column }` override
- Hero title uses `clamp()` scaling — no overflow at any width
- Stats row stacks vertically at ≤768px
- Feature grid forced to `1fr` single column at ≤768px
- Container padding: `0 16px` → `0 12px` → `0 10px` across breakpoints
- `padding-bottom: calc(72px + env(safe-area-inset-bottom))` — no content behind bottom nav
- All buttons/nav items meet 44–52px touch targets
- `overflow-x: hidden` on html/body — no horizontal scroll
- Admin grid single column at ≤768px
- Reviews stats bar reflows: 5-col → 3-col → 2-col

## Data (as of 2026-05-11)

- ChromaDB: ~2,500+ pairs (vocabulary + sentences + grammar + proverbs + corrections)
- Feedback log: `data/feedback/feedback_log.jsonl`
- Training pairs: `data/training/training_pairs.jsonl`
- Dataset export: `data/training/dataset_export_YYYY-MM-DD.jsonl`
