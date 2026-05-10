# CLAUDE.md — Luganda AI Studio

> This file defines how Claude must behave on this project.
> Read this before touching any file. Follow every rule exactly.

---

## 1. Mission

Build a practical, local-first AI application that helps users:
- Translate between Luganda and English
- Search a structured Luganda knowledge base
- Learn Luganda through interactive teaching mode
- Improve translation quality through human feedback and data collection

This is a real product, not a demo. Every decision must be practical,
minimal, and safe for the actual machine it runs on.

---

## 2. Machine Constraints

| Component | Spec |
|---|---|
| OS | Windows 64-bit |
| CPU | Intel Core i7-11800H |
| RAM | 16 GB |
| GPU | NVIDIA RTX 3050 Laptop GPU |
| VRAM | 4 GB |

### Rules from these constraints

- Do NOT recommend training a large model from scratch
- Do NOT assume cloud hardware unless clearly labelled as optional
- Prefer local-first or lightweight hybrid approaches
- All AI features must be realistic for 4 GB VRAM or CPU-only

---

## 3. Current Stack

### Backend

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Server | Uvicorn |
| Vector DB | ChromaDB |
| Embeddings | MiniLM (sentence-transformers) |
| Language | Python 3.10+ |

**Start command:**
```
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

**API base:** `http://127.0.0.1:8000`

### Frontend

| Layer | Technology |
|---|---|
| Type | Static HTML / CSS / JS |
| Served at | `/app/` via FastAPI StaticFiles |
| Build step | None required |
| Fonts | Fraunces (display) + DM Sans (body) via Google Fonts |

### API Routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/translate` | Luganda ↔ English translation |
| GET | `/api/v1/knowledge/search` | Semantic search across collections |
| GET | `/api/v1/knowledge/stats` | Collection record counts |

### Translation Payload

```json
{
  "text": "hello",
  "direction": "en_to_lg"
}
```

Direction values: `en_to_lg` or `lg_to_en`

### Translation Response

```json
{
  "input_text": "hello",
  "direction": "en_to_lg",
  "translated_text": "Oli otya",
  "match_type": "exact",
  "confidence": 1.0,
  "matched_collection": "vocabulary",
  "matched_source_file": "vocab_01.json",
  "status": "success",
  "message": "Exact match found."
}
```

Status values: `success` or `not_found`

### Translation Pipeline (backend)

```
Input
  → exact match       (confidence: 1.00)
  → normalized match  (confidence: 0.98)
  → partial match     (confidence: 0.85)
  → semantic match    (confidence: variable, threshold 0.50)
  → not_found
```

### ChromaDB Collections

| Collection | Purpose |
|---|---|
| vocabulary | Word-level pairs |
| sentences | Full sentence pairs |
| grammar | Grammar rules and notes |
| proverbs | Luganda proverbs |

---

## 4. Frontend Pages — Current State

| Page | URL | Status |
|---|---|---|
| Dashboard | `/app/index.html` | Working |
| Translate | `/app/translate.html` | Working + Quality Mode |
| Search | `/app/search.html` | Working |

### translate.html — Quality Features

The translate page now includes:
- Result chips: direction, confidence %, match type, collection
- Feedback buttons: ✓ Correct / ✗ Wrong / 🔁 Needs Review
- Expected output field: text input to record correct translation
- Session history: running log of all translations in this session
- Export JSON: downloads full session as structured training data

---

## 5. Folder Structure

```
Luganda_AI_Studio/
├── backend/
│   ├── main.py                          ← FastAPI app entry point
│   ├── core/
│   │   └── config.py                    ← App settings + paths
│   ├── api/
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py
│   │       ├── knowledge.py             ← Search + stats routes
│   │       ├── translate.py             ← Translation route
│   │       ├── feedback.py              ← POST /api/v1/feedback
│   │       ├── teach.py                 ← Teaching mode cards
│   │       └── chat.py                  ← Chat assistant
│   ├── services/
│   │   ├── ingestion/
│   │   │   ├── loader.py               ← Dataset JSON loader
│   │   │   ├── embedder.py             ← MiniLM embedding model
│   │   │   └── indexer.py              ← ChromaDB indexing
│   │   └── translation/
│   │       ├── schemas.py              ← Request/response models
│   │       └── service.py              ← Translation logic
│   └── db/
│       └── chroma_client.py            ← ChromaDB client singleton
├── frontend/
│   ├── index.html
│   ├── translate.html                   ← Quality Mode + feedback to API
│   ├── search.html
│   ├── teach.html
│   └── styles.css
├── scripts/                             ← Automation scripts
│   ├── download_datasets.py            ← Phase 1: fetch Flores-200, JW300
│   ├── ingest_dataset.py               ← Phase 1: load JSON into ChromaDB
│   └── process_feedback.py             ← Phase 3: corrections → ChromaDB + training
├── data/
│   ├── chromadb/                        ← ChromaDB persistent storage
│   ├── datasets/                        ← Downloaded + cleaned datasets
│   ├── feedback/                        ← User feedback JSONL logs
│   └── training/                        ← Accumulated training pairs for NLLB
├── datasets/                            ← Original hand-curated data
│   ├── vocabulary/
│   ├── sentences/
│   ├── grammar/
│   └── proverbs/
├── docs/
│   ├── project_plan.md
│   └── training-plan.md                 ← Model training roadmap (3 phases)
├── CLAUDE.md                            ← This file
└── README.md
```

---

## 6. Behaviour Rules

### Always do these

- Read the relevant files before writing any code
- Design before coding — explain what and why first
- Return FULL files only — never snippets or partials
- Label every file exactly as shown in Section 8
- Explain what changed, why it changed, and what to test
- End every response with clear next steps
- Flag missing information instead of guessing
- Keep changes minimal and focused on the stated task

### Never do these

- Do not jump into code without a plan
- Do not return partial files or say "same as before"
- Do not recommend training a large model from scratch
- Do not assume we have enough Luganda data
- Do not touch files unrelated to the current task
- Do not silently invent missing requirements
- Do not ignore machine constraints

---

## 7. Approval-First Workflow

For every task, follow this order:

```
1. Inspect relevant files
2. Report what exists — confirmed facts only
3. Identify the real problem clearly
4. Propose the fix in plain language
5. State exactly which files will change
6. Wait for explicit approval if the change is large or risky
7. Then implement — full files only
8. Show exact before/after for every change
9. Provide browser test steps
10. State what to do next
```

**When to ask for approval before coding:**
- Any change touching more than 2 files
- Any change to the backend translation pipeline
- Any change to ChromaDB schema or collections
- Any structural refactor
- Any new dependency being added

**When to proceed without asking:**
- Single-file frontend fixes already discussed
- URL or field name corrections already confirmed
- CSS or copy fixes with no logic impact

---

## 8. File Return Format

Every file must be labelled exactly like this:

```
FILE: path/to/file.py
ACTION: NEW
```

or

```
FILE: path/to/file.py
ACTION: REPLACE
```

Every returned file must include:
- All imports
- All functions and classes — complete, not summarised
- All exports
- Everything needed to run the file independently
- Comments marking new or changed sections with: `# CHANGED` or `// CHANGED`

---

## 9. Data Rules

Luganda data is limited. Always treat it carefully.

| Data type | Where it lives | How it is used |
|---|---|---|
| Vocabulary pairs | ChromaDB `vocabulary` | Translation + search |
| Sentence pairs | ChromaDB `sentences` | Translation + search |
| Grammar notes | ChromaDB `grammar` | Search only |
| Proverbs | ChromaDB `proverbs` | Search only |
| Original datasets | `datasets/` (vocabulary, sentences, grammar, proverbs) | Source JSON files loaded by `loader.py` |
| Imported datasets | `data/datasets/` | Downloaded Flores-200, JW300, etc. Ingested by `ingest_dataset.py` |
| User feedback | `data/feedback/feedback_log.jsonl` | Verdicts saved by feedback API, processed by `process_feedback.py` |
| Correction pairs | `data/training/corrections.jsonl` | Full records for audit |
| Training pairs | `data/training/training_pairs.jsonl` | Minimal format for future NLLB-200 LoRA fine-tuning |

**Never delete or overwrite ChromaDB data without explicit approval.**

---

## 10. What Is Coming Next

> Last updated: 2026-05-10

| Feature | Priority | Notes |
|---|---|---|
| ~~Run Phase 1 data scaling~~ | ~~NOW~~ | ✅ Done — Flores-200 ingested. ChromaDB 492 → 2,500+ pairs |
| ~~NLLB-200 neural fallback~~ | ~~High~~ | ✅ Done — `nllb_service.py` + pipeline Pass 3. Benchmarked 2026-04-19 |
| ~~Feedback loop~~ | ~~High~~ | ✅ Done — Correction UI → API → ChromaDB. Tested 2026-04-19 |
| ~~Feedback API POST~~ | ~~High~~ | ✅ Done — `feedback.py` appends to `feedback_log.jsonl` |
| ~~Data ingestion pipeline~~ | ~~High~~ | ✅ Done — `download_datasets.py`, `ingest_dataset.py`, `process_feedback.py` |
| ~~Quality metrics~~ | ~~High~~ | ✅ Done — Session Summary card live in `translate.html` |
| ~~Feedback review page~~ | ~~High~~ | ✅ Done — `reviews.html` + `GET /api/v1/feedback`. Built 2026-04-19 |
| ~~Teaching mode~~ | ~~NOW~~ | ✅ Done — `teach.html` full flash card + quiz mode. 5 endpoints. Confirmed 2026-04-19 |
| ~~CSV ingestor~~ | ~~High~~ | ✅ Done — `scripts/ingest_csv.py`. Auto-detect separator, column aliases. Built 2026-04-19 |
| ~~PDF parser~~ | ~~High~~ | ✅ Done — `scripts/ingest_pdf.py`. Table + line pattern modes, direction auto-detect. Built 2026-04-19 |
| ~~OpenRouter API integration~~ | ~~High~~ | ✅ Done — `openrouter_service.py` + pipeline Pass 4.5. Default: gemma-2-9b-it:free. Built 2026-05-10 |
| ~~Luganda TTS (Meta MMS)~~ | ~~High~~ | ✅ Done — `mms_tts_service.py` + `/api/v1/tts`. 🔊 on translate + teach pages. Built 2026-05-10 |
| ~~Dataset export pipeline~~ | ~~High~~ | ✅ Done — `scripts/export_dataset.py`. HuggingFace-compatible, cleaned, versioned. Built 2026-05-10 |
| Set OPENROUTER_API_KEY in .env | **NOW** | Required to activate OpenRouter. Free key at openrouter.ai |
| Install TTS deps | **NOW** | `pip install transformers scipy` then test 🔊 button |
| ~~Admin dashboard~~ | ~~Next~~ | ✅ Done — `admin.html` + `GET /api/v1/admin/status`. 5 cards. Built 2026-05-10 |
| ~~Test infrastructure~~ | ~~High~~ | ✅ Done — pytest + 11 tests (admin + openrouter tracking). Built 2026-05-10 |
| Multilingual embeddings upgrade | Medium | Switch MiniLM → paraphrase-multilingual-MiniLM-L12-v2. Requires full re-embed |
| TTS audio caching | Low | Cache common words so teach.html plays instantly after first load |
| Test suite expansion | Low | Add degradation tests for admin; translate pipeline tests |
| LoRA fine-tuning | Low | Only when 500+ correction pairs. Script not yet built |
| Publish dataset to HuggingFace | Low | Run export_dataset.py, create HF dataset repo, upload |

## 11. Current State Snapshot

> Updated: 2026-05-10 (session B)

**What works right now:**
- Translation pipeline: exact → normalized → partial → semantic → OpenRouter API → NLLB-200 neural
- Luganda TTS: 🔊 speaker button on translate + teach pages (Meta MMS, real Luganda voice)
- Search across vocabulary, sentences, grammar, proverbs collections
- Feedback collection: users rate translations, corrections auto-ingest into ChromaDB
- Dataset export: `scripts/export_dataset.py` produces clean HuggingFace-compatible JSONL
- Reviews page: admin view of all submitted feedback with stats and filters
- Session quality metrics: live summary on translate page
- Admin dashboard: `/app/admin.html` — system health, collection counts, feedback stats, pipeline status
- Test suite: 11 tests passing (`pytest tests/ -v`)

**What does NOT exist yet:**
- OPENROUTER_API_KEY not yet added to .env — OpenRouter silently skipped until this is done
- TTS dependencies not yet installed — `pip install transformers scipy` required
- Multilingual embeddings (MiniLM → paraphrase-multilingual-MiniLM-L12-v2)

**Data:**
- ChromaDB: ~2,500+ pairs (vocabulary + sentences + grammar + proverbs + corrections)
- Feedback log: `data/feedback/feedback_log.jsonl` (grows with each user correction)
- Training pairs: `data/training/training_pairs.jsonl` (for future LoRA fine-tuning)
- Dataset export: `data/training/dataset_export_YYYY-MM-DD.jsonl` (run export_dataset.py to generate)
