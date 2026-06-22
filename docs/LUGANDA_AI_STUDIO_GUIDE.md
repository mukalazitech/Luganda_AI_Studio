# Luganda AI Studio — Complete Guide
> Generated: 2026-06-06 | Patrick Mukalazi (patricktwin1@gmail.com)

---

## What Is This?

**Luganda AI Studio** is Patrick's AI-powered Luganda ↔ English language app.

It is a real product — not a demo — built to:
- Translate between Luganda and English instantly
- Help people learn Luganda through flashcards and teaching mode
- Search a structured Luganda knowledge base
- Collect user corrections to improve translation quality over time
- Eventually become a trained AI model for the Luganda language

The app runs on a local machine (your Windows PC) and is published online at **https://lugandastudio.com**

---

## My Goals for Luganda AI Studio

| Goal | What It Means |
|------|---------------|
| **Language preservation** | Luganda is spoken by millions in Uganda. This app helps preserve and spread it digitally. |
| **Production quality** | Not a toy. Real translations, real TTS voice, real learning tools. |
| **Train a custom AI model** | Eventually fine-tune NLLB-200 on verified Luganda data collected from real users. |
| **Free to use** | Hosted on lugandastudio.com — accessible to anyone. |
| **Grow the dataset** | Every correction a user submits becomes training data for the future model. |

---

## Current Status (June 2026)

| Feature | Status |
|---------|--------|
| Translation (Luganda ↔ English) | ✅ LIVE |
| Text-to-Speech (hear Luganda words spoken) | ✅ LIVE |
| Speech-to-Text (speak into mic, get text) | ✅ LIVE |
| Teaching mode (flashcards + quiz) | ✅ LIVE |
| Semantic search | ✅ LIVE |
| User feedback / correction loop | ✅ LIVE |
| Admin dashboard | ✅ LIVE |
| Hosted online at lugandastudio.com | ✅ LIVE (Railway) |
| 149 automated tests | ✅ ALL PASSING |
| Dataset: 492 embedded records in ChromaDB | ✅ LIVE |
| Custom AI model (LoRA fine-tuning) | 🔴 PENDING — need 500+ corrections first |
| HuggingFace dataset upload | 🔴 PENDING |

---

## How the App Works (Simple Explanation)

When you type a word in English (e.g., "thank you"):

```
1. Exact match check         → finds "thank you" in our word list instantly
2. Normalized match check    → tries lowercase, plural variations
3. Partial match check       → "thanks" matches "thank you / thanks"
4. AI semantic match         → finds the closest meaning using embeddings
5. OpenRouter AI fallback    → asks an online AI model (free)
6. NLLB-200 local model      → uses our on-device neural translation model
7. Not found                 → tells the user nothing was found
```

The system tries 6 different methods before giving up — so it catches much more than a simple dictionary would.

---

## The Stack (What It's Built With)

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | FastAPI (Python) | Fast, modern, easy to extend |
| Vector database | ChromaDB | Stores AI embeddings for semantic search |
| Embeddings | MiniLM (multilingual) | Understands meaning, not just exact words |
| Neural translation | NLLB-200-distilled-600M | Meta's real African languages model |
| Text-to-Speech | Meta MMS (Luganda voice) | Real Luganda pronunciation |
| Speech-to-Text | OpenAI Whisper | Converts your voice to text |
| AI fallback | OpenRouter (Gemma 2 free) | Online AI when local methods fail |
| Frontend | HTML + CSS + JavaScript | Simple, no framework needed |
| Hosting | Railway.app | Cloud platform, always-on |
| Domain | lugandastudio.com (Cloudflare) | Professional address |

---

## Where the App Lives

| Environment | Location | How to Use |
|------------|----------|------------|
| **Live online** | https://lugandastudio.com | Anyone can visit this URL |
| **Local dev** | `D:\projects\Luganda_AI_Studio\` | Your Windows PC |
| **GitHub** | github.com/mukalazitech/Luganda_AI_Studio | Source code |
| **Railway** | Project: `acceptable-essence` | Cloud hosting |
| **Deploy** | `railway up` from project folder | Push new version to cloud |

---

## Railway Problem & Fix (June 2026)

### What Happened
Railway stopped serving the app. The app went offline.

### Why This Happens on Railway
- Railway's free/hobby tier **sleeps apps** after inactivity
- GitHub auto-deploy was **broken** when the repo was transferred from `MukalaziPatrick` → `mukalazitech`
- The Railway GitHub App lost connection to the repo

### Three Options (Choose One)

#### Option A — Fix Railway (Recommended for now)
Re-connect Railway to the new GitHub repo and redeploy.

**Steps:**
1. Open Railway dashboard → Project `acceptable-essence`
2. Go to Service → `Luganda_AI_Studio` → Settings → Source
3. Disconnect old GitHub connection
4. Connect to `mukalazitech/Luganda_AI_Studio`
5. Trigger a manual deploy
6. OR just run: `cd D:\projects\Luganda_AI_Studio && railway up`

**Cost:** Free on hobby tier (sleeps after 30 min inactivity)
**Uptime:** App wakes in ~10-20 seconds when someone visits

#### Option B — Move Back to Local + Cloudflare Tunnel
Run the app on your PC, use Cloudflare tunnel to make it public.

**Pros:** 
- Always fast (runs on your RTX 3050)
- TTS is instant, NLLB is faster
- No Railway downtime

**Cons:**
- App goes offline when your PC is off or asleep
- Requires Cloudflare tunnel to be running

**To start locally:**
```
cd D:\projects\Luganda_AI_Studio
start.bat
```

#### Option C — Upgrade Railway (Paid)
Pay Railway ~$5/month for always-on hosting with no sleep.

---

## Data Overview

| Data | Where | Amount |
|------|-------|--------|
| Vocabulary pairs | ChromaDB `vocabulary` collection | ~424 records |
| Sentence pairs | ChromaDB `sentences` collection | ~110 records |
| Grammar notes | ChromaDB `grammar` collection | ~28 records |
| Proverbs | ChromaDB `proverbs` collection | ~60 records |
| User corrections | `data/training/corrections.jsonl` | Growing |
| Training pairs | `data/training/training_pairs.jsonl` | Need 500 for LoRA |

---

## The Road to a Custom Luganda AI Model

```
Phase 1 (NOW): Collect data
  → Users translate, rate results, submit corrections
  → Every ✗ "Wrong" click = 1 training pair
  → Target: 500 verified correction pairs

Phase 2 (When 500+ pairs): Fine-tune the model
  → Run: python scripts/finetune_lora.py
  → Uses LoRA — fine-tunes on 4 GB VRAM RTX 3050
  → Creates a custom adapter on top of NLLB-200
  → Better Luganda translations specific to Uganda usage

Phase 3 (Future): Publish
  → Upload dataset to HuggingFace
  → Share model publicly
  → Open-source Uganda's first Luganda AI dataset
```

---

## Key Commands

```bash
# Start the app locally
cd D:\projects\Luganda_AI_Studio
start.bat

# Deploy to Railway (cloud)
cd D:\projects\Luganda_AI_Studio
railway up

# Run all tests
cd D:\projects\Luganda_AI_Studio
venv\Scripts\activate
python -m pytest tests/ -v

# Re-index ChromaDB (after adding new vocabulary files)
python scripts/reembed.py

# Check LoRA training readiness
python scripts/finetune_lora.py --check

# Export dataset for HuggingFace
python scripts/export_dataset.py
```

---

## Key Files

| File | Purpose |
|------|---------|
| `start.bat` | Start everything locally |
| `backend/main.py` | FastAPI entry point |
| `backend/services/translation/service.py` | 6-pass translation logic |
| `backend/services/tts/mms_tts_service.py` | Luganda TTS voice |
| `scripts/reembed.py` | Rebuild ChromaDB after data changes |
| `scripts/finetune_lora.py` | Train the custom Luganda model |
| `HANDOFF.md` | Full session handoff notes |
| `CLAUDE.md` | Rules for AI coding sessions |

---

## Next Steps (Priority Order)

1. **Fix Railway** — get the app back online at lugandastudio.com
2. **Wire GitHub auto-deploy** — so pushes to `mukalazitech/Luganda_AI_Studio` auto-deploy
3. **Test TTS + STT on mobile** — open lugandastudio.com on Android phone
4. **Add more vocabulary** — add JSON files to `datasets/vocabulary/`, run `reembed.py`
5. **Collect 500 correction pairs** — users submit via ✗ button on translate page
6. **Run LoRA fine-tuning** — when 500+ pairs ready
7. **Upload to HuggingFace** — publish Uganda's first Luganda AI dataset

---

*Luganda AI Studio — built by Patrick Mukalazi, Kampala, Uganda*
*Goal: Preserve and empower the Luganda language through AI*
