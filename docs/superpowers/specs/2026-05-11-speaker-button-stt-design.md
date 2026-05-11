# Design Spec: Speaker Button Redesign + STT Architecture
**Date:** 2026-05-11  
**Status:** Approved  
**Scope:** Phase 1 (speaker button fix) + Phase 2 blueprint (STT + audio data collection)

---

## 1. Problem Statement

The current TTS speaker button (`🔊`) is a small plain-bordered square with no label. It is:
- Not recognisable to new or non-technical users
- Too small to tap comfortably on mobile
- Visually invisible — it blends into the output card

Additionally, the app has no speech-to-text (STT) capability, meaning users cannot speak Luganda into the app. This is a missed opportunity for both usability and data collection.

---

## 2. Phase 1 — Speaker Button Redesign (Implement Now)

### Goal
Make the TTS button immediately recognisable and tappable for all users, including beginners.

### Design Decision
Replace the emoji-only button with a **labeled pill button**: `🔊 Listen`

- Background: `--lime` (the app's existing accent color, already used for active states)
- Text: `🔊 Listen` — universally understood
- Padding: sufficient to meet 44px touch target minimum on mobile
- States:
  - Default: `🔊 Listen` — lime background
  - Speaking: `⏳ Speaking…` — dimmed, disabled
  - After playback: returns to `🔊 Listen`

### Files Changing
| File | Change |
|---|---|
| `frontend/styles.css` | Update `.tts-btn` — add background, label layout, speaking state |
| `frontend/translate.html` | Update button markup + JS state labels |
| `frontend/teach.html` | Update both TTS buttons (card + quiz) + JS state labels |

### What Does NOT Change
- TTS backend route (`/api/v1/tts`) — no changes
- `mms_tts_service.py` — no changes
- Audio is still streamed in-memory, not stored (TTS output is not training data)

---

## 3. Audio Storage — Confirmed Facts

**TTS (text-to-speech) audio is never stored.** The backend synthesizes WAV bytes in memory and streams them to the browser. The browser creates a temporary blob URL, plays it, then discards it. Nothing is written to disk.

**For reference — where audio will live in Phase 2:**
```
data/
└── audio/
    ├── recordings/              ← raw .wav files from user mic
    └── transcription_log.jsonl  ← paired (audio, text) training records
```

---

## 4. Phase 2 — STT Service Architecture (Blueprint, Not Built Yet)

### Goal
- Let users speak Luganda into the app on translate + teach pages
- Transcribe speech to text automatically
- Save every recording as a (audio, text) training pair
- Build a growing Luganda STT dataset from real app usage

### New Backend Service
**File:** `backend/services/stt/whisper_service.py`  
**Model:** `sulaimank/whisper-small-luganda-400hr-all` (HuggingFace)  
- Fine-tuned Whisper-small on 400 hours of Luganda audio
- Runs on CPU (compatible with 4GB VRAM machine)
- Lazy-loaded on first request (same pattern as `mms_tts_service.py`)

### New API Route
**File:** `backend/api/routes/stt.py`  
`POST /api/v1/stt`

```json
Request:
{
  "audio": "<base64-encoded-wav>",
  "source": "translate" | "teach"
}

Response:
{
  "text": "Oli otya",
  "confidence": 0.91,
  "transcription_source": "api" | "local"
}
```

### Hybrid Transcription Logic
1. Try free Whisper API endpoint first (fast, no local resources)
2. On failure or offline → fall back to `sulaimank/whisper-small-luganda-400hr-all` locally on CPU
3. Save `.wav` to `data/audio/recordings/` regardless of which path was used
4. Append full record to `data/audio/transcription_log.jsonl`

### Transcription Log Schema
```json
{
  "id": "rec_1715432100",
  "file": "data/audio/recordings/rec_1715432100.wav",
  "source": "translate",
  "transcribed_text": "Oli otya",
  "transcription_source": "api",
  "confidence": 0.91,
  "user_confirmed": true,
  "user_correction": null,
  "timestamp": "2026-05-11T10:35:00"
}
```

### Frontend Mic Button
Added to both `translate.html` and `teach.html`:
- `🎙 Speak` button next to the input field
- Click once: starts recording, button shows `🔴 Recording…`
- Click again: stops recording, sends audio to `/api/v1/stt`
- Transcribed text fills the input field automatically
- User can edit the text before submitting — edits saved as `user_confirmed: true` with `user_correction`

### Files Changing in Phase 2
| File | Change |
|---|---|
| `backend/services/stt/__init__.py` | NEW |
| `backend/services/stt/whisper_service.py` | NEW — lazy Whisper loader + hybrid logic |
| `backend/api/routes/stt.py` | NEW — POST /api/v1/stt |
| `backend/main.py` | Register new STT route |
| `backend/core/config.py` | Add audio storage paths |
| `frontend/translate.html` | Add mic button + recording JS |
| `frontend/teach.html` | Add mic button + recording JS |

---

## 5. Dataset Improvement Path

### How the app feeds back into improving Whisper

```
User speaks → audio saved → transcribed → user confirms/corrects
                                                ↓
                        data/audio/transcription_log.jsonl grows
                                                ↓
                   (future) scripts/export_audio_dataset.py
                   produces HuggingFace-compatible dataset
                                                ↓
               Fine-tune sulaimank/whisper-small on YOUR Luganda data
                                                ↓
               Model gets better at YOUR users' real Luganda speech
```

### Other improvement areas across the app

| Area | Current gap | Improvement path |
|---|---|---|
| STT | Does not exist | Phase 2 Whisper integration |
| Translation | ~2,500 pairs | Ingest more CSV/PDF sources |
| Embeddings | English-only MiniLM | Upgrade to `paraphrase-multilingual-MiniLM-L12-v2` |
| TTS | Works, uncached | Cache common words for instant playback on teach page |
| Feedback loop | Corrections saved | Already feeds ChromaDB — keep growing |
| Audio dataset | Nothing yet | Phase 2 data collection builds from zero |

### HuggingFace Model — Seed Dataset
The `sulaimank/whisper-small-luganda-400hr-all` model page should be checked for a linked dataset. If the author published the 400-hour audio dataset publicly, it can be used as seed data immediately — before any users record anything. This would give the local Whisper model a strong starting point before fine-tuning on app-collected data.

**Action:** Check https://huggingface.co/sulaimank/whisper-small-luganda-400hr-all for dataset links in the model card.

---

## 6. Machine Constraints (from CLAUDE.md)

- CPU: Intel Core i7-11800H
- RAM: 16 GB
- GPU: NVIDIA RTX 3050 Laptop, 4 GB VRAM
- Whisper-small runs on CPU at ~1-2s per short phrase — fully compatible
- No cloud hardware assumed

---

## 7. Out of Scope

- Training a model from scratch
- Real-time streaming transcription
- Speaker diarization
- Multi-speaker support
