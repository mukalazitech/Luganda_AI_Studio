# GPU Selection Guide + NotebookLM Research Assets
> For: Patrick Mukalazi | Context: Running AI locally for Luganda Studio + future AI Coding Agent

---

## Why GPUs Matter for Your Projects

You currently have:
- **RTX 3050 Laptop (4 GB VRAM)** — runs NLLB-200, TTS, Whisper STT on your PC
- **Future need** — RunPod GPU rental for the AI Coding Agent (heavier models)

This guide helps you understand what each GPU tier can run and what to buy/rent next.

---

## GPU Tier Breakdown for AI (2025/2026)

### Tier 1: Entry (What You Have Now)
**RTX 3050 Laptop — 4 GB VRAM**

| Can Run | Cannot Run |
|---------|-----------|
| NLLB-200 distilled 600M (translation) ✅ | LLaMA 3 70B |
| Whisper STT (speech recognition) ✅ | Mistral 22B |
| Meta MMS TTS (Luganda voice) ✅ | Full fine-tuning from scratch |
| LoRA fine-tuning (with 8-bit quantization) ✅ | Stable Diffusion XL |
| LLaMA 3.2 3B (with quantization) ✅ | |
| Phi-3 Mini ✅ | |
| ChromaDB + MiniLM embeddings ✅ | |

**Verdict:** Good enough for Luganda AI Studio. Not enough for heavy coding agents.

---

### Tier 2: Mid-Range (RunPod Rental for Projects)
**RTX 4080 / RTX 3090 — 16–24 GB VRAM**

| Can Run | Monthly Cost (RunPod) |
|---------|----------------------|
| LLaMA 3 8B full precision | ~$0.39/hr |
| Mistral 7B / Mixtral | ~$0.39/hr |
| DeepSeek Coder 7B | ~$0.39/hr |
| CodeLlama 13B | ~$0.55/hr |
| Stable Diffusion XL | ~$0.39/hr |
| LoRA fine-tuning (any 7B model) | ~$0.39/hr |

**Verdict:** Best price/performance for your AI Coding Agent on RunPod.

---

### Tier 3: High-End (Cloud only — not local)
**A100 / H100 — 40–80 GB VRAM**

| Can Run | Monthly Cost (RunPod) |
|---------|----------------------|
| LLaMA 3 70B full | ~$2.49/hr |
| Training from scratch (small models) | ~$2.49/hr |
| Batch inference at scale | ~$2.49/hr |

**Verdict:** Only needed when you start a commercial AI product at scale. Skip for now.

---

## For Your AI Coding Agent (Equator Labs Plan)

The plan calls for RunPod + Ollama. Here is the recommended setup:

**Recommended GPU:** RTX 4090 (24 GB VRAM) on RunPod
**Cost:** ~$0.74/hr → run only during coding sessions (~2 hrs/day = ~$44/month)

**Models that fit on 24 GB VRAM:**
- `deepseek-coder:33b` — best code model, fits in 24 GB with 4-bit
- `codellama:34b` — good alternative
- `llama3:8b` — lightweight, fast responses

**Cheaper option:** RTX 3090 (24 GB) at ~$0.39/hr
- Same VRAM as 4090, slower compute
- Good for testing before committing to 4090

---

## NotebookLM Setup Instructions

### Step 1: Prepare Your Sources

Add these documents to NotebookLM as sources:
1. `docs/LUGANDA_AI_STUDIO_GUIDE.md` (this project)
2. `docs/AI_MODEL_TEST_PROMPTS.md` (testing guide)
3. `docs/GPU_NOTEBOOKLM_GUIDE.md` (this file)
4. The Tom's Hardware GPU Hierarchy page (already in your notebook)
5. The Clarifai "Best GPUs for Deep Learning" article (already in your notebook)

### Step 2: Generate Audio Overview

In NotebookLM → Studio tab → click "Generate Audio Overview"

NotebookLM will create a 10-15 minute podcast-style audio discussion about your sources.

**Good for:**
- Listening while you walk/commute
- Getting a high-level understanding before reading details
- Sharing with non-technical collaborators

### Step 3: Useful Questions to Ask (Chat Tab)

**About GPUs:**
- "What GPU should I buy for running LLaMA 3 8B locally at home?"
- "Compare RTX 4090 vs A100 for LoRA fine-tuning — which is better value?"
- "What is the minimum VRAM needed to run DeepSeek Coder 33B?"
- "Can I run Whisper STT and NLLB-200 at the same time on 4 GB VRAM?"
- "What is the difference between VRAM and RAM for AI models?"

**About Luganda AI Studio:**
- "What does the 6-pass translation pipeline do?"
- "How many training pairs do I need before LoRA fine-tuning?"
- "What is the difference between NLLB-200 and OpenRouter for translation?"

**About model training:**
- "What is LoRA and how does it make fine-tuning possible on small GPUs?"
- "How many Luganda training pairs do I realistically need for a useful language model?"
- "What is the HuggingFace Hub and how do I publish a dataset there?"

---

## GPU Quick Reference Card

```
YOUR PC NOW:
  RTX 3050 Laptop (4 GB) — runs Luganda AI Studio ✅

RUNPOD RENTAL FOR CODING AGENT:
  RTX 4090 (24 GB) — $0.74/hr — best for DeepSeek Coder 33B
  RTX 3090 (24 GB) — $0.39/hr — cheaper, slightly slower
  RTX 4080 (16 GB) — $0.55/hr — runs 7B-13B models well

NEVER NEED (too expensive for solo dev):
  A100 80GB — $2.49/hr — only for startups training from scratch
  H100 80GB — $3.99/hr — enterprise training only

KEY NUMBERS TO REMEMBER:
  7B parameter model  → needs ~8 GB VRAM (4-bit quantized: ~4 GB)
  13B parameter model → needs ~14 GB VRAM (4-bit: ~8 GB)
  33B parameter model → needs ~35 GB VRAM (4-bit: ~20 GB)
  70B parameter model → needs ~75 GB VRAM (4-bit: ~40 GB)

YOUR RTX 3050 (4 GB) can run:
  ✅ Models up to ~3B parameters (4-bit)
  ✅ NLLB-200 distilled (translation)
  ✅ Whisper base/small (STT)
  ✅ MMS TTS (Luganda voice)
  ❌ LLaMA 3 8B full precision
  ✅ LLaMA 3.2 3B (4-bit quantized)
```

---

## Recommended Learning Path (via NotebookLM Audio)

Listen to these topics in order to build your GPU/AI knowledge:

1. **"What is VRAM and why does it matter for AI?"** — foundation
2. **"GPU benchmarks for deep learning 2025"** — from Tom's Hardware source
3. **"Best GPUs for running LLMs locally"** — from Clarifai source
4. **"LoRA fine-tuning explained simply"** — how you'll train Luganda model
5. **"HuggingFace Hub for developers"** — where you'll publish your dataset

---

## Action Plan: Railway Fix + Going Forward

### Immediate (today):

**Option 1 — Quick redeploy via CLI:**
```powershell
cd D:\projects\Luganda_AI_Studio
railway up
```
This pushes the current code to Railway and restarts the service.
Takes about 2-3 minutes.

**Option 2 — Check Railway status first:**
```powershell
railway status
```

**Option 3 — Run locally while Railway is fixed:**
```
Double-click: D:\projects\Luganda_AI_Studio\start.bat
App available at: http://127.0.0.1:8000/app/index.html
```

### This Week:
- [ ] Get lugandastudio.com back online (Railway redeploy)
- [ ] Wire GitHub auto-deploy to mukalazitech repo
- [ ] Test TTS on Android phone
- [ ] Add 10 new vocabulary JSON entries, run reembed.py

### This Month:
- [ ] Collect 50+ user correction pairs
- [ ] Upload dataset snapshot to HuggingFace (even partial)
- [ ] Fund RunPod for AI Coding Agent Phase A testing

---

*Patrick Mukalazi — Kampala, Uganda — building AI for Africa*
