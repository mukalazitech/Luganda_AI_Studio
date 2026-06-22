# Phase 0 — Foundation Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the three foundation bugs blocking the Luganda app before any UI/UX work starts: the production dictionary only has 4 vocabulary words instead of hundreds, the correction-save button returns a server error, and the repo carries 21MB+ of dead weight from an abandoned seeding approach.

**Architecture:** Run the existing local re-embed script against the full `datasets/vocabulary/*.json` set, push the result to the live Railway volume via direct file upload (the only method that has worked previously — `railway.json`'s `start` field is overridden by a dashboard-level custom start command), fix a one-character route mismatch between frontend and backend for feedback submission, then delete the now-unused seed-script machinery.

**Tech Stack:** Python (FastAPI, ChromaDB, sentence-transformers), vanilla JS frontend, Railway CLI.

---

## Task 1: Re-embed the full vocabulary locally

**Files:**
- Run: `scripts/reembed.py` (no changes needed — already correct)
- Read-only verify: `datasets/vocabulary/*.json` (12 files)

- [ ] **Step 1: Stop the local FastAPI server if running**

If you have `uvicorn backend.main:app` running locally, stop it (Ctrl+C). The reembed script checks port 8000 and will warn you if something is still bound to it.

- [ ] **Step 2: Run the re-embed script**

```bash
cd D:\projects\Luganda_AI_Studio
python scripts/reembed.py
```

Expected output ends with a summary table showing non-zero counts for `vocabulary`, `sentences`, `grammar`, `proverbs`. Vocabulary should jump from 4 to several hundred (12 JSON files × dozens of entries each — `animals.json` alone has 53).

- [ ] **Step 3: Verify the local ChromaDB now has the full vocabulary**

```bash
python -c "from backend.db.chroma_client import get_chroma_client; c = get_chroma_client(); print(c.get_collection('vocabulary').count())"
```

Expected: a number in the hundreds, not 4.

- [ ] **Step 4: Spot-check the previously-wrong entries**

```bash
python -c "
from backend.db.chroma_client import get_chroma_client
c = get_chroma_client().get_collection('vocabulary')
r = c.get(where={'luganda': 'Embwa'})
print(r['metadatas'])
"
```

Expected: a result showing `english: Dog` (confirms the "dog → embwa" bug is data-side and now fixed by re-embedding the audited source file).

- [ ] **Step 5: Commit (local data isn't committed, but note the local-only re-embed happened)**

No commit needed here — `data/chromadb/` is local runtime data, not tracked in git. Proceed to Task 2 to ship it to Railway.

---

## Task 2: Push the re-embedded ChromaDB to the live Railway volume

**Files:** none changed — this is a deployment operation against the running container's mounted volume.

- [ ] **Step 1: List current collection directories to upload**

```bash
cd D:\projects\Luganda_AI_Studio
ls data/chromadb/
```

You'll see `chroma.sqlite3` plus one UUID-named directory per collection (4 collections = at least 4 UUID dirs, likely more from prior runs — only the current ones matter).

- [ ] **Step 2: Upload chroma.sqlite3 directly (overwrite)**

```bash
MSYS_NO_PATHCONV=1 railway service files upload --service Luganda_AI_Studio data/chromadb/chroma.sqlite3 /app/data/chromadb/chroma.sqlite3 --overwrite
```

Expected: upload success message. (The `MSYS_NO_PATHCONV=1` prefix stops Git Bash from mangling the `/app/...` remote path into a Windows path — confirmed necessary in the prior session.)

- [ ] **Step 3: Upload each UUID collection directory individually**

For each UUID directory listed in Step 1 (do NOT upload the parent `data/chromadb` folder as a whole — that nests one level too deep, a confirmed bug in upload-into-existing-dir behavior):

```bash
MSYS_NO_PATHCONV=1 railway service files upload --service Luganda_AI_Studio data/chromadb/<uuid> /app/data/chromadb/<uuid> --overwrite
```

Repeat for every UUID directory present locally.

- [ ] **Step 4: Verify live via the status endpoint**

```bash
curl https://lugandastudio.com/api/v1/knowledge/status
```

Expected: `vocabulary` count in the hundreds (matching Task 1 Step 3's local count), not 4.

- [ ] **Step 5: Verify live translation now resolves "dog" to "embwa" directly**

```bash
curl "https://lugandastudio.com/api/v1/translate?text=dog&direction=en_to_lg"
```

(Adjust query params to match the actual translate endpoint signature if different — check `backend/api/routes/translate.py` for the exact param names if this 404s.)

Expected: a direct vocabulary match returning "embwa" at high confidence, not a 52%-confidence unrelated sentence.

- [ ] **Step 6: Spot-check "Emesse" now quizzes as "Rat"**

In the live UI at https://lugandastudio.com/app/teach.html, run the quiz until "Emesse" appears, or query directly:

```bash
curl "https://lugandastudio.com/api/v1/knowledge/search?q=Emesse&top_k=1"
```

Expected: `english: Rat` (or whatever the audited `animals.json` source says — re-confirm against `datasets/vocabulary/animals.json` if this entry isn't in that specific file).

No commit needed — this task is a live-data operation, not a code change.

---

## Task 3: Fix the correction-save route mismatch

**Files:**
- Modify: `frontend/translate.html:266`
- Test: manual (no automated frontend test harness in this repo)

**Root cause:** `backend/api/routes/feedback.py` router is mounted with `prefix="/api/v1/feedback"` (confirmed in `backend/main.py:113`) and its POST handler is declared at `"/"` (confirmed in `backend/api/routes/feedback.py:114`), so the real route is `/api/v1/feedback/` (trailing slash). The frontend's `FEEDBACK_URL` constant at `frontend/translate.html:266` is `'/api/v1/feedback'` (no trailing slash) — FastAPI treats these as different routes without `redirect_slashes` matching, causing the "Could not reach server" error. This is the same class of bug as the earlier translate-405 fix (`@router.post("/")` vs frontend posting without the slash).

- [ ] **Step 1: Confirm the exact current line**

```bash
grep -n "FEEDBACK_URL" frontend/translate.html
```

Expected: `266:const FEEDBACK_URL  = '/api/v1/feedback';`

- [ ] **Step 2: Fix the constant to include the trailing slash**

In `frontend/translate.html`, change line 266 from:

```javascript
const FEEDBACK_URL  = '/api/v1/feedback';
```

to:

```javascript
const FEEDBACK_URL  = '/api/v1/feedback/';
```

- [ ] **Step 3: Test locally**

```bash
cd D:\projects\Luganda_AI_Studio
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open `http://127.0.0.1:8000/app/translate.html`, translate any word, click "Wrong", type a correction, click "Save Correction".

Expected: a success indicator (not "Could not reach server"), and a new line appended to `data/feedback/feedback_log.jsonl`:

```bash
tail -n 1 data/feedback/feedback_log.jsonl
```

- [ ] **Step 4: Commit**

```bash
git add frontend/translate.html
git commit -m "fix: correct feedback endpoint trailing slash mismatch"
```

- [ ] **Step 5: Deploy the fix to Railway**

```bash
railway up --service Luganda_AI_Studio
```

If it times out on upload (known issue with the ~188MB repo), retry:

```bash
timeout 280 railway up --service Luganda_AI_Studio
```

Check `railway deployment list` — top row should read `SUCCESS`.

- [ ] **Step 6: Verify live**

On https://lugandastudio.com/app/translate.html, repeat Step 3's manual test against production. Expected: success, no red error.

---

## Task 4: Remove dead seed-script weight

**Files:**
- Delete: `seed_data/` (directory, ~21MB)
- Delete: `scripts/seed_volume_if_empty.py`
- Modify: `railway.json`

**Rationale:** The actual fix for the empty-volume problem (prior session) was a direct `railway service files upload` against the running container, not this build-time seed step. The seed script never ran in production because Railway's dashboard-level custom start command silently overrides `railway.json`'s `start` field. Keeping this code risks a future session assuming it's functional.

- [ ] **Step 1: Delete the seed_data directory**

```bash
cd D:\projects\Luganda_AI_Studio
rm -rf seed_data/
```

- [ ] **Step 2: Delete the seed script**

```bash
rm scripts/seed_volume_if_empty.py
```

- [ ] **Step 3: Revert railway.json to a plain start command**

Read current `railway.json`:

```json
{
  "build": {
    "builder": "nixpacks"
  },
  "start": "python scripts/seed_volume_if_empty.py && uvicorn backend.main:app --host 0.0.0.0 --port $PORT"
}
```

Replace with:

```json
{
  "build": {
    "builder": "nixpacks"
  },
  "start": "uvicorn backend.main:app --host 0.0.0.0 --port $PORT"
}
```

Note: this field has no effect in production anyway (the dashboard custom start command overrides it), but it should still reflect reality for local/other-environment use and to avoid confusing future readers.

- [ ] **Step 4: Verify nothing else references the deleted files**

```bash
grep -rn "seed_volume_if_empty\|seed_data" --include="*.py" --include="*.json" --include="*.md" .
```

Expected: no remaining references in active code (handoff/memory docs mentioning the history are fine to leave as-is — they're historical record, not live code).

- [ ] **Step 5: Commit**

```bash
git add -A railway.json
git rm -r --cached seed_data/ scripts/seed_volume_if_empty.py 2>/dev/null
git commit -m "chore: remove dead seed-script weight, real fix was direct volume upload"
```

- [ ] **Step 6: Deploy and verify the image is smaller / still boots correctly**

```bash
railway up --service Luganda_AI_Studio
```

Check `railway deployment list` for `SUCCESS`, then hit `https://lugandastudio.com/api/v1/knowledge/status` once more to confirm the app still boots with the full vocabulary count intact (this is a deploy of code-only changes; the volume data from Task 2 is untouched since volumes persist independently of deploys).

---

## Task 5: Patrick-only manual cleanup (cannot be done by an agent)

**Files:** none — Railway CLI operation blocked for agents by harness safety gate.

- [ ] **Step 1 (Patrick runs this, not the agent):** Delete the stray nested leftover from the original mis-targeted upload:

```bash
railway service files delete --service Luganda_AI_Studio /app/data/chromadb/chromadb
```

This is harmless if left alone (the app never reads that nested path) — low priority, do whenever convenient.

---

## Final Verification (run after all tasks complete)

- [ ] `curl https://lugandastudio.com/api/v1/knowledge/status` → vocabulary count in the hundreds
- [ ] Live UI: translating "dog" → "embwa" as a direct vocab hit, not a 52%-confidence sentence
- [ ] Live UI: "Emesse" quizzes with its corrected gloss
- [ ] Live UI: Translate → Wrong → type correction → Save Correction → success, not "Could not reach server"
- [ ] `seed_data/`, `scripts/seed_volume_if_empty.py` no longer exist in the repo; `railway.json` has the plain start command
- [ ] All changes committed and deployed (`railway deployment list` shows `SUCCESS` as the top row)

Once all boxes are checked, Phase 0 is done. Resume the roadmap at Phase 1 (UI/UX redesign) via the `polish-and-price` skill — see `project_luganda_app_roadmap.md` memory and `C:\Users\patri\.claude\plans\luganda-ai-studio-should-reflective-candy.md` for full Phase 1 scope.
