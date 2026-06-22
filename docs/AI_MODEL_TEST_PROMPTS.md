# Luganda AI Studio — AI Model Test Prompts
> Use these to test the translation API and evaluate model quality

---

## How to Use These Prompts

**Option 1 — Browser (easiest)**
Open https://lugandastudio.com/app/translate.html and type the words manually.

**Option 2 — API (copy-paste into terminal)**
```bash
# Test English → Luganda
curl -X POST https://lugandastudio.com/api/v1/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "hello", "direction": "en_to_lg"}'

# Test Luganda → English
curl -X POST https://lugandastudio.com/api/v1/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "webale", "direction": "lg_to_en"}'
```

**Option 3 — Local API (if running locally)**
Replace `https://lugandastudio.com` with `http://127.0.0.1:8000`

---

## Test Set 1: Basic Greetings (Exact Match Expected)

These should return confidence 1.0 (exact match). If they don't, the ChromaDB data needs re-indexing.

| Test Word | Direction | Expected Translation | Expected Confidence |
|-----------|-----------|---------------------|---------------------|
| hello | en_to_lg | Oli otya | 1.0 |
| thank you | en_to_lg | Webale nyo | 1.0 |
| good morning | en_to_lg | Wasuze otya | 1.0 |
| goodbye | en_to_lg | Weeraba | 1.0 |
| yes | en_to_lg | Yee | 1.0 |
| no | en_to_lg | Nedda | 1.0 |
| webale | lg_to_en | Thank you | 1.0 |
| oli otya | lg_to_en | How are you | 1.0 |

---

## Test Set 2: Semantic Match (AI Understanding Test)

These test whether the AI understands meaning, not just exact words.
Expected confidence: 0.50–0.85 (semantic match type).

| Test Word | Direction | What To Look For |
|-----------|-----------|-----------------|
| thanks | en_to_lg | Should match "thank you" → Webale nyo |
| morning greeting | en_to_lg | Should find wasuze otya |
| how do you do | en_to_lg | Should find oli otya |
| I am fine | en_to_lg | Should find "I am well" equivalent |
| greet someone | en_to_lg | Should suggest greeting words |

---

## Test Set 3: Harder Words (NLLB Neural Model Test)

These test the NLLB-200 neural fallback. If the word is not in ChromaDB,
the app falls back to the on-device AI translation model.
Expected match_type: "nllb" or "openrouter"

| Test Word | Direction | Notes |
|-----------|-----------|-------|
| entrepreneurship | en_to_lg | Complex English word — tests NLLB |
| democracy | en_to_lg | Political word — tests NLLB |
| agriculture | en_to_lg | Common in Uganda — should be in DB |
| okusomesa | lg_to_en | "to teach" — tests Luganda → English |
| ekitabo | lg_to_en | "book" — tests Luganda → English |
| omusawo | lg_to_en | "doctor" — tests Luganda → English |

---

## Test Set 4: TTS Voice Test (Audio Test)

Open the translate page and click the 🔊 button after each translation.

**Words to test (good for hearing Luganda pronunciation):**
- webale (thank you)
- oli otya (how are you)
- wasuze otya (good morning)
- bannange (my friends / people)
- mukwano (friend / love)
- gamba (speak / say)

**What to check:**
- First click: takes 5-10 seconds (model loads) — NORMAL
- Second click: instant (cached) — must be instant
- The pronunciation should sound like real Luganda

---

## Test Set 5: Teaching Mode Test

Open `/app/teach.html` and use the flashcard system.

**What to check:**
1. Cards load vocabulary words correctly
2. Quiz mode shows 4 answer options
3. Correct answer shows green highlight
4. Wrong answer shows red + correct answer
5. TTS 🔊 button works on flashcards

---

## Test Set 6: Search Test

Open `/app/search.html` — type a word and see semantic results.

| Search Query | Expected Results |
|-------------|-----------------|
| greet | Should find hello, goodbye, morning greeting |
| family | Should find mother, father, child words |
| food | Should find eating, drinking words |
| farm | Should find agriculture, land, cattle |

---

## API Response Format Reference

When you call the API, you get back JSON like this:

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

**Match types explained:**

| match_type | Meaning | Confidence |
|-----------|---------|-----------|
| exact | Perfect word match | 1.0 |
| normalized | Lowercase/trimmed match | 0.98 |
| partial | Word found inside phrase | 0.85 |
| semantic | AI embedding similarity | 0.50–0.80 |
| openrouter | Online AI model used | 0.75 |
| nllb | On-device NLLB-200 model used | 0.70 |
| not_found | Nothing matched | — |

---

## Quality Score Tracking

Run these 10 "golden" tests every session to track model quality over time.

**Copy-paste batch test (PowerShell):**
```powershell
$words = @("hello","thank you","good morning","goodbye","yes","no","water","food","mother","father")
foreach ($word in $words) {
    $body = @{text=$word; direction="en_to_lg"} | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "https://lugandastudio.com/api/v1/translate" -Method POST -Body $body -ContentType "application/json"
    Write-Host "$word → $($result.translated_text) [$($result.match_type), $($result.confidence)]"
}
```

**Expected results (all should be exact or normalized match):**
- hello → Oli otya [exact, 1.0]
- thank you → Webale nyo [exact, 1.0]
- good morning → Wasuze otya [exact, 1.0]

---

## NotebookLM Prompts (for Audio Overviews)

Use these when asking NotebookLM to generate audio summaries about the project:

1. "Explain how the 6-pass translation pipeline works in simple terms, suitable for a non-technical audience"
2. "What is NLLB-200 and why is it important for African languages like Luganda?"
3. "Explain what ChromaDB does and why vector databases are used for AI search"
4. "What is LoRA fine-tuning and how does it let small computers train AI models?"
5. "Compare the GPU options for running AI locally on a laptop: what should someone with a 4 GB VRAM card realistically expect?"

---

*Save this file and add to NotebookLM as a source for an overview podcast about Luganda AI Studio*
