# Luganda AI — Road Plan (June 2026)

> Direction-setting doc. Written after a full audit of the actual repo on 2026-06-06.
> Thesis: **the data + model layer is the real business; the app is the wedge that feeds it.**

---

## 1. Where you actually are (ground truth, not the CLAUDE.md claims)

The **machinery is built**. The **fuel tank is almost empty.**

**What genuinely works (confirmed in the repo):**

- Full FastAPI backend, deployed live on Railway (not just localhost anymore).
- Translation pipeline: exact → normalized → partial → semantic → OpenRouter → NLLB.
- STT (Whisper), TTS (Meta MMS), search, teach mode, chat, feedback API, admin dashboard.
- `OPENROUTER_API_KEY` is now set in `.env`.
- Scripts already exist for the hard parts: `download_datasets.py`, `ingest_csv.py`, `ingest_pdf.py`, `process_feedback.py`, `export_dataset.py`, `finetune_lora.py`, `upload_to_huggingface.py`.
- 11 pytest tests.

**The uncomfortable truth — your actual data:**

| Asset | Reality on disk | What you'd need for a real model |
|---|---|---|
| Audio recordings | **9 files, <1 MB** (just your own mic tests) | hundreds of *hours* |
| Training pairs | **47 rows** | 500+ to even start LoRA; thousands to matter |
| Correction pairs | 47 | same |
| Feedback log | 173 entries | fine for now |
| Source datasets | vocabulary 12 files, sentences **2**, grammar 4, proverbs 1 | 10–100× more |
| `knowledge_base/pdfs/` | **empty** (just a README) | dozens of Luganda PDFs |
| ChromaDB | 6.3 MB (~2,500 indexed pairs) | the one thing that's OK |

**Translation: you have built a beautiful engine with almost no fuel.** Every "what's missing" answer below is really about fuel.

---

## 2. What's missing (ranked by what actually blocks the business)

1. **Data volume — the #1 gap and the whole moat.** Audio corpus is effectively zero. Parallel EN↔LG corpus is tiny. This is what makes Luganda AI valuable *and* what nobody else has bothered to build.
2. **A data-collection pipeline (the "agents").** Scripts can *ingest* data, but nothing *goes and gets* it. There's no harvest → transcribe → review → log loop running on its own.
3. **A human-correction flywheel at scale.** In-app feedback exists, but there's no cheap, high-volume way to get native speakers correcting transcripts/translations (a bot).
4. **A fine-tuning routine.** `finetune_lora.py` exists but can't do anything useful at 47 pairs. Needs the data first, then RunPod in bursts.
5. **A monetization surface.** No API keys/auth, no usage metering, no billing, no first paying use case wired up.
6. **Scheduled automation.** None of the above runs on a schedule yet — it's all manual.

---

## 3. The thesis (the direction)

There are two businesses inside "Luganda AI":

- **The App** — consumer language learning. Not defensible; anyone can build it.
- **The Data/Model Layer** — a clean Luganda speech + parallel corpus and the speech-to-text / translation models trained on it. Luganda is low-resource; Google/Whisper are weak at it. **This is scarce and defensible.**

**Direction: build the data/model layer as the product, and keep the app as a thin wedge** that (a) proves the models work and (b) harvests corrections from real users for free.

Spend money on: people correcting data, and short GPU bursts. Do **not** spend money on: idle GPU, or polishing app features nobody's using yet.

---

## 4. The road plan (phased, with real actions)

### Phase 0 — Unblock & set the baseline  *(this week)*
- Install TTS deps (`pip install transformers scipy`) and confirm 🔊 works end to end.
- Confirm the live Railway URL is healthy (`/api/v1/health`) and the frontend points at it.
- Write a tiny `corpus_status.py` that prints real counts (audio hours, training pairs, corrections, parallel pairs). **You can't grow what you don't measure.**
- **Decision gate:** confirm the data-layer-first thesis (Section 8).

### Phase 1 — The Data Factory  *(weeks 1–3)* ← the core of everything
Goal: go from ~0 to a *real* audio + text corpus, on autopilot.
- Pick sources: Luganda YouTube (sermons, news, talk shows, music with lyrics), radio archives, Bukedde/newspapers, Luganda Wikipedia, Bible/Quran in Luganda, government PDFs.
- Build a **harvest agent**: downloads new audio + text from a source list, stores raw, logs metadata to Supabase/Airtable.
- Build an **auto-transcribe step**: runs Whisper over new audio, writes transcript + confidence, flags anything below ~0.7 for human review.
- Build an **ingest step**: cleaned text → ChromaDB + parallel-pair file.
- Wire all three as **scheduled tasks** (nightly) so the corpus grows while you sleep.
- **Target:** first 20–50 hours of transcribed Luganda audio + a few thousand parallel sentences.

### Phase 2 — The Correction Flywheel  *(weeks 3–6)*
Goal: cheap, high-volume human correction — the thing that actually makes the data good.
- Build a **Telegram/WhatsApp bot**: sends a native speaker a transcript or translation, they fix it, it logs the correction. Pay micro-rewards (airtime/Mobile Money).
- Keep the in-app feedback loop feeding the same corrections file.
- **Target:** cross 500+ correction pairs → fine-tuning becomes possible.

### Phase 3 — Fine-tune in bursts  *(when Phase 2 target hit)*
- Spin RunPod **only for the weekend**: fine-tune Whisper on corrected audio + NLLB LoRA on parallel pairs. Shut it down after.
- Benchmark against the baseline (you already have `benchmark_nllb.py` and `nllb-benchmark.md`).
- Push the dataset to HuggingFace (`upload_to_huggingface.py`) — credibility + a licensing asset.

### Phase 4 — Productize for money  *(parallel, from week 4)*
- Wrap translation/STT/TTS as an **API with keys + usage metering**.
- **First customer = yourself:** dogfood it inside Farm Beacon (Luganda content/voice) and Business Yoo. Proof before you sell.
- Then pitch NGOs, agritech, media subtitling, researchers.

### Phase 5 — App as wedge  *(ongoing, low priority)*
- Keep the app shippable and clean, but treat it as a demo + data-harvest funnel, not the main event.

---

## 5. How your existing stack maps to this

| Tool | Role in the new plan |
|---|---|
| **RunPod** | Off by default. Rent GPU only for Phase 3 fine-tuning bursts, then kill it. |
| **Hermes + Claude agents (scheduled)** | Your 24/7 data-factory workers: nightly harvest, transcribe, queue-for-review, and a line in your morning briefing ("corpus grew by X hours / Y pairs"). |
| **Bots (Telegram/WhatsApp)** | The correction flywheel front-end (Phase 2). |
| **Supabase/Airtable** | Corpus catalog + review queue + correction log. |
| **OpenRouter** | Cheap LLM fallback for translation + cleanup, already wired. |

---

## 6. Monetization milestones

1. Dogfood inside Farm Beacon / Business Yoo (validates the API). — *Phase 4*
2. First paid Luganda transcription/translation gig (NGO, media, research). — *after Phase 3*
3. Luganda API on a usage/subscription plan. — *after Phase 4*
4. Dataset licensing + HuggingFace credibility. — *after Phase 3*
5. App subscriptions (freemium) as the long-tail consumer line.

Defensibility order: **API/model > dataset > app**.

---

## 7. Skill candidates to extract (per your standing rule)

As we build these, turn the repeatable ones into reusable skills:

- **`corpus-harvest`** — the nightly source → audio/text → log loop.
- **`auto-transcribe-review`** — Whisper transcribe + low-confidence flagging.
- **`finetune-burst`** — spin RunPod, fine-tune, benchmark, shut down (a runbook-style skill).
- **`corpus-status`** — one-command snapshot of corpus size and growth.

---

## 8. The one decision that sets everything

**Confirm or reject the thesis:** *data/model layer is the product, app is the wedge.*

- If **yes** → we start Phase 0 + 1 (build the data factory). This is my recommendation and the evidence (empty audio dir) backs it.
- If **app-first** → we instead polish the consumer app and grow data slowly from app users only (slower moat, easier launch).

Riskiest assumption either way: that you can get enough *cheap, reliable* human correction in Uganda to make the models good. Phase 2's bot exists to de-risk exactly that — so we should test it early.

---

*Next step after you confirm direction: I build the Phase 1 harvest agent + scheduled task, and run the cross-project routines audit you asked for.*
