# Luganda App — Phase 1 UX Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the 3 concrete gaps found in the Phase 1 UX design spec (`docs/superpowers/specs/2026-06-23-luganda-app-phase1-ux-design.md`) against Duolingo/Merriam-Webster/NKENNE: a client-side daily streak + session XP system for Teach (the single biggest gap — zero gamification exists anywhere in the codebase today), friendlier Home hero copy (currently exposes raw internal record counts), and warmer Translate empty/error-state copy (currently reads like a database error).

**Architecture:** Pure frontend, vanilla JS, no backend changes. The streak is `localStorage`-backed (a `luganda_streak_v1` JSON blob: `{count, lastDate}`), incremented once per calendar day when a Teach session completes (`doneScreen` in `teach.html`), and displayed as a small pill in the mobile topbar across Home/Translate/Search/Teach via a shared inline script block (matching this codebase's existing pattern of per-page inline `<script>` rather than a bundler). Session XP is an in-memory counter reset each session, shown only on the Teach done-screen — no backend table needed, matching the "don't bolt on backend work prematurely" principle from the design spec.

**Tech Stack:** Vanilla HTML/CSS/JS (no framework), existing CSS variable system in `frontend/styles.css`, `localStorage` for persistence.

---

## Task 1: Streak storage module (shared logic)

**Files:**
- Create: `frontend/streak.js`
- Modify: `frontend/index.html:1` (add script tag), `frontend/translate.html:1` (add script tag), `frontend/search.html:1` (add script tag), `frontend/teach.html:1` (add script tag)

This is pure logic with no DOM dependency, so it's testable by hand in a browser console before wiring into pages.

- [ ] **Step 1: Create the streak module**

```javascript
// frontend/streak.js
// Shared daily-streak + session-XP logic for Luganda AI Studio.
// Streak persists across days via localStorage; XP is in-memory per session.

const STREAK_KEY = 'luganda_streak_v1';

function _todayStr() {
  return new Date().toISOString().slice(0, 10); // 'YYYY-MM-DD'
}

function _yesterdayStr() {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  return d.toISOString().slice(0, 10);
}

function getStreak() {
  try {
    const raw = localStorage.getItem(STREAK_KEY);
    if (!raw) return { count: 0, lastDate: null };
    const parsed = JSON.parse(raw);
    if (typeof parsed.count !== 'number' || typeof parsed.lastDate !== 'string') {
      return { count: 0, lastDate: null };
    }
    return parsed;
  } catch (e) {
    return { count: 0, lastDate: null };
  }
}

// Call once when a Teach session completes (flash or quiz "Session Complete!" screen).
// Returns the updated streak object. Increments at most once per calendar day;
// resets to 1 if the last completed day was before yesterday (streak broken).
function recordSessionComplete() {
  const today = _todayStr();
  const streak = getStreak();

  if (streak.lastDate === today) {
    // Already recorded today — no change.
    return streak;
  }

  const yesterday = _yesterdayStr();
  const newCount = (streak.lastDate === yesterday) ? streak.count + 1 : 1;
  const updated = { count: newCount, lastDate: today };
  localStorage.setItem(STREAK_KEY, JSON.stringify(updated));
  return updated;
}

// Renders the streak count into any element with id="streakPill" on the current page.
// Safe to call on pages that don't have the element (no-op).
function renderStreakPill() {
  const el = document.getElementById('streakPill');
  if (!el) return;
  const streak = getStreak();
  el.textContent = streak.count > 0 ? `🔥 ${streak.count}` : '🔥 0';
  el.title = streak.count > 0
    ? `${streak.count} day streak — keep it up!`
    : 'Complete a Teach session to start your streak';
}

document.addEventListener('DOMContentLoaded', renderStreakPill);
```

- [ ] **Step 2: Manually verify the module logic in a browser console**

Open any page locally (`python -m http.server` from `frontend/` or via the running FastAPI app at `http://127.0.0.1:8000/app/index.html`), open DevTools console, and run:

```javascript
localStorage.removeItem('luganda_streak_v1');
console.log(getStreak()); // { count: 0, lastDate: null }
console.log(recordSessionComplete()); // { count: 1, lastDate: '<today>' }
console.log(recordSessionComplete()); // { count: 1, lastDate: '<today>' } — same day, no double-increment
```

Expected: exactly the values shown in the comments above.

- [ ] **Step 3: Verify streak-break logic by faking an old date**

```javascript
localStorage.setItem('luganda_streak_v1', JSON.stringify({ count: 5, lastDate: '2020-01-01' }));
console.log(recordSessionComplete()); // { count: 1, lastDate: '<today>' } — old streak broken, resets to 1
```

Expected: `count` resets to `1` because `2020-01-01` is neither today nor yesterday.

- [ ] **Step 4: Verify streak-continue logic by faking yesterday's date**

```javascript
const y = new Date(); y.setDate(y.getDate() - 1);
localStorage.setItem('luganda_streak_v1', JSON.stringify({ count: 5, lastDate: y.toISOString().slice(0,10) }));
console.log(recordSessionComplete()); // { count: 6, lastDate: '<today>' } — streak continues
```

Expected: `count` increments to `6`.

- [ ] **Step 5: Add the script tag to all 4 pages**

In `frontend/index.html`, add this line immediately before the closing `</head>` tag (after the existing `<link rel="stylesheet" href="/app/styles.css" />` line):

```html
  <script src="/app/streak.js"></script>
```

Repeat the identical addition in `frontend/translate.html`, `frontend/search.html`, and `frontend/teach.html` — same insertion point (right after the `styles.css` link, before `</head>`).

- [ ] **Step 6: Commit**

```bash
cd D:\projects\Luganda_AI_Studio
git add frontend/streak.js frontend/index.html frontend/translate.html frontend/search.html frontend/teach.html
git commit -m "feat: add shared daily-streak module for Teach gamification"
```

---

## Task 2: Streak pill in the mobile topbar

**Files:**
- Modify: `frontend/index.html:45-49`, `frontend/translate.html:45-49`, `frontend/search.html:44-48`, `frontend/teach.html:44-48`
- Modify: `frontend/styles.css` (add `.streak-pill` style near the existing `.chip` rules around line 427)

The mobile topbar markup is currently (e.g. `frontend/index.html:44-48`):

```html
  <!-- Mobile topbar -->
  <header class="mobile-topbar">
    <span class="mobile-topbar-title">Luganda AI Studio</span>
    <button class="theme-icon-btn" id="mobileThemeBtn" onclick="toggleTheme()">☀</button>
  </header>
```

- [ ] **Step 1: Add the `.streak-pill` CSS rule**

In `frontend/styles.css`, immediately after the `.chip-amber` rule (around line 439), add:

```css
.streak-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--amber-bg);
  color: var(--amber);
  border: 1px solid var(--amber-border);
  font-size: 12px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  margin-right: 8px;
}
```

- [ ] **Step 2: Insert the pill into each page's mobile topbar**

In `frontend/index.html`, change:

```html
  <header class="mobile-topbar">
    <span class="mobile-topbar-title">Luganda AI Studio</span>
    <button class="theme-icon-btn" id="mobileThemeBtn" onclick="toggleTheme()">☀</button>
  </header>
```

to:

```html
  <header class="mobile-topbar">
    <span class="mobile-topbar-title">Luganda AI Studio</span>
    <div style="display:flex;align-items:center;">
      <span class="streak-pill" id="streakPill">🔥 0</span>
      <button class="theme-icon-btn" id="mobileThemeBtn" onclick="toggleTheme()">☀</button>
    </div>
  </header>
```

Apply the same pattern to `frontend/translate.html` (topbar title "Translate"), `frontend/search.html` (topbar title "Search"), and `frontend/teach.html` (topbar title "Teach") — same `<div>` wrapper with `id="streakPill"` inserted, only the `mobile-topbar-title` text differs per page (keep each page's existing title unchanged).

- [ ] **Step 3: Verify no layout shift**

Reload each of the 4 pages on a phone-width viewport (DevTools device toolbar, e.g. iPhone SE 375px). Expected: the pill renders immediately at `🔥 0` (since `streak.js`'s `DOMContentLoaded` listener runs before paint settles), no visible jump after load. If the count changes after a Teach session, reloading any page should immediately show the new persisted value with no flash of `🔥 0` first followed by a jump — `renderStreakPill()` runs synchronously off `localStorage`, not a network fetch, so this is guaranteed by design.

- [ ] **Step 4: Commit**

```bash
cd D:\projects\Luganda_AI_Studio
git add frontend/index.html frontend/translate.html frontend/search.html frontend/teach.html frontend/styles.css
git commit -m "feat: show daily streak pill in mobile topbar across all pages"
```

---

## Task 3: Wire streak increment + session XP into Teach's done-screen

**Files:**
- Modify: `frontend/teach.html` (the `finishSession()` function and the `doneScreen` markup at lines 103-129)

First, locate the exact current `finishSession()` implementation:

- [ ] **Step 1: Confirm the current finishSession function (shared by both flash and quiz modes)**

```bash
cd D:\projects\Luganda_AI_Studio
grep -n "function finishSession" -A 30 frontend/teach.html
```

Current implementation (lines 446-472):

```javascript
function finishSession() {
  const seen  = countCorrect + countWrong;
  const score = seen > 0 ? Math.round((countCorrect / seen) * 100) : 0;

  document.getElementById('doneScore').textContent      = score + '%';
  document.getElementById('summaryCorrect').textContent = countCorrect;
  document.getElementById('summaryWrong').textContent   = countWrong;
  document.getElementById('summarySeen').textContent    = seen;
  document.getElementById('progressFill').style.width   = '100%';

  const reviewBtn = document.getElementById('reviewMissedBtn');
  reviewBtn.style.display = (mode === 'flash' && missedCards.length > 0) ? 'inline-flex' : 'none';

  // Save progress to backend
  fetch('/api/v1/teach/progress', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      cards_seen:   seen,
      correct:      countCorrect,
      wrong:        countWrong,
      session_date: new Date().toISOString(),
    }),
  }).catch(() => {});  // Fire and forget — not critical

  showScreen('done');
}
```

This single function is shared by both flash and quiz modes (driven by the shared `countCorrect`/`countWrong` counters), so the streak/XP wiring only needs to be added here once — not duplicated per mode.

- [ ] **Step 2: Add an XP counter element to the done-screen markup**

In `frontend/teach.html`, the current done-screen markup (lines 103-129) is:

```html
      <!-- DONE -->
      <div class="state-screen" id="doneScreen">
        <div class="done-card">
          <div class="state-icon">🎉</div>
          <div class="state-title">Session Complete!</div>
          <div class="done-score" id="doneScore">—%</div>
          <div class="done-score-label">accuracy this session</div>
          <div class="done-stats">
            <div class="done-stat correct-stat">
              <div class="done-stat-value" id="summaryCorrect">0</div>
              <div class="done-stat-label">Correct</div>
            </div>
            <div class="done-stat wrong-stat">
              <div class="done-stat-value" id="summaryWrong">0</div>
              <div class="done-stat-label">Wrong</div>
            </div>
            <div class="done-stat">
              <div class="done-stat-value" id="summarySeen">0</div>
              <div class="done-stat-label">Seen</div>
            </div>
          </div>
          <div class="done-buttons">
            <button class="btn-primary"   onclick="boot()">New Session</button>
            <button class="btn-secondary" id="reviewMissedBtn" onclick="reviewMissed()" style="display:none">Review Missed</button>
          </div>
        </div>
      </div>
```

Change it to add a streak/XP summary line directly under `done-score-label`:

```html
      <!-- DONE -->
      <div class="state-screen" id="doneScreen">
        <div class="done-card">
          <div class="state-icon">🎉</div>
          <div class="state-title">Session Complete!</div>
          <div class="done-score" id="doneScore">—%</div>
          <div class="done-score-label">accuracy this session</div>
          <div class="chip chip-amber" id="doneStreakLine" style="margin-bottom:16px;">🔥 Streak: — · +— XP</div>
          <div class="done-stats">
            <div class="done-stat correct-stat">
              <div class="done-stat-value" id="summaryCorrect">0</div>
              <div class="done-stat-label">Correct</div>
            </div>
            <div class="done-stat wrong-stat">
              <div class="done-stat-value" id="summaryWrong">0</div>
              <div class="done-stat-label">Wrong</div>
            </div>
            <div class="done-stat">
              <div class="done-stat-value" id="summarySeen">0</div>
              <div class="done-stat-label">Seen</div>
            </div>
          </div>
          <div class="done-buttons">
            <button class="btn-primary"   onclick="boot()">New Session</button>
            <button class="btn-secondary" id="reviewMissedBtn" onclick="reviewMissed()" style="display:none">Review Missed</button>
          </div>
        </div>
      </div>
```

- [ ] **Step 3: Add an XP-award helper and wire it into finishSession**

In the `<script>` block of `frontend/teach.html`, near the other session-state variables (around line 219-235, where `countCorrect`, `countWrong`, `quizCorrect` etc. are declared), add:

```javascript
// XP: 10 per correct answer, 2 per attempt regardless of outcome (encourages trying).
function calculateSessionXP(correctCount, totalSeen) {
  return (correctCount * 10) + (totalSeen * 2);
}
```

Then modify `finishSession()` (lines 446-472, shown above) to add the streak+XP wiring right before `showScreen('done')`. Change:

```javascript
  const reviewBtn = document.getElementById('reviewMissedBtn');
  reviewBtn.style.display = (mode === 'flash' && missedCards.length > 0) ? 'inline-flex' : 'none';

  // Save progress to backend
```

to:

```javascript
  const reviewBtn = document.getElementById('reviewMissedBtn');
  reviewBtn.style.display = (mode === 'flash' && missedCards.length > 0) ? 'inline-flex' : 'none';

  const sessionXP = calculateSessionXP(countCorrect, seen);
  const updatedStreak = recordSessionComplete();
  document.getElementById('doneStreakLine').textContent =
    `🔥 Streak: ${updatedStreak.count} day${updatedStreak.count === 1 ? '' : 's'} · +${sessionXP} XP`;
  renderStreakPill();

  // Save progress to backend
```

(Using `countCorrect` and the already-computed `seen` local variable directly, rather than re-parsing them back out of the DOM — simpler and avoids a redundant round-trip through `textContent`.)

- [ ] **Step 4: Manual end-to-end test**

```bash
cd D:\projects\Luganda_AI_Studio
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open `http://127.0.0.1:8000/app/teach.html`, clear `localStorage` streak key first (DevTools console: `localStorage.removeItem('luganda_streak_v1')`), then complete one full flash-card session (answer all cards via "Got It" / "Try Again" until the "Session Complete!" screen appears).

Expected: the done-screen shows `🔥 Streak: 1 day · +N XP` where N matches `(correct × 10) + (seen × 2)`. Reload the page (or navigate to Home) — the topbar streak pill should now show `🔥 1`.

- [ ] **Step 5: Verify same-day re-run doesn't double-increment**

Without changing the system date, click "New Session" and complete a second session immediately.

Expected: the done-screen still shows `🔥 Streak: 1 day` (not 2) — same calendar day, per the `recordSessionComplete()` logic from Task 1.

- [ ] **Step 6: Repeat the test for Quiz mode**

Switch to Quiz mode (🧠 Quiz toggle), complete a 10-question quiz session.

Expected: same streak/XP line appears correctly on the quiz done-screen (the done-screen markup is shared between flash and quiz modes per the existing code).

- [ ] **Step 7: Commit**

```bash
git add frontend/teach.html
git commit -m "feat: award session XP and increment daily streak on Teach session complete"
```

---

## Task 4: Friendlier Home hero copy (remove raw stat-count framing)

**Files:**
- Modify: `frontend/index.html:54-79`

Current markup (lines 54-79):

```html
      <!-- Hero -->
      <section class="hero">
        <div class="hero-kicker">Luganda AI Studio</div>
        <h1 class="hero-title">
          Translate.<br>
          Learn.<br>
          <span class="hero-underline">Communicate.</span>
        </h1>
        <p class="hero-desc">AI-powered tools for the Luganda language — built to run on your machine.</p>
        <!-- CHANGED: Improved hero layout with button and theme toggle separated for mobile -->
        <div class="hero-actions mt-8">
          <a href="translate.html" class="btn-primary hero-cta">Start Translating →</a>
          <div class="theme-pill" id="heroPill" style="align-self: center;">
            <button class="theme-pill-btn" id="heroLight" onclick="setTheme('light')">☀ Light</button>
            <button class="theme-pill-btn" id="heroDark"  onclick="setTheme('dark')">🌙 Dark</button>
          </div>
        </div>
      </section>

      <!-- Stats row -->
      <div class="stats-row" id="statsRow">
        <div class="stat-item"><span class="stat-value" id="statVocab">—</span><span class="stat-label">Vocabulary pairs</span></div>
        <div class="stat-item"><span class="stat-value" id="statSentences">—</span><span class="stat-label">Sentence pairs</span></div>
        <div class="stat-item"><span class="stat-value" id="statGrammar">—</span><span class="stat-label">Grammar notes</span></div>
        <div class="stat-item"><span class="stat-value" id="statProverbs">—</span><span class="stat-label">Proverbs</span></div>
      </div>
```

Per the design spec, replace "built to run on your machine" (a developer-facing phrase) with a trust line, and replace the 4-way raw-count breakdown with a single combined, human-readable line — keep the underlying `/api/v1/knowledge/status` fetch (it already sums correctly elsewhere), just present it as one sentence instead of 4 separate technical labels.

- [ ] **Step 1: Replace the hero description and stats row**

Change the block above to:

```html
      <!-- Hero -->
      <section class="hero">
        <div class="hero-kicker">Luganda AI Studio</div>
        <h1 class="hero-title">
          Translate.<br>
          Learn.<br>
          <span class="hero-underline">Communicate.</span>
        </h1>
        <p class="hero-desc">Verified by native Luganda speakers — works offline, no account needed to start.</p>
        <!-- CHANGED: Improved hero layout with button and theme toggle separated for mobile -->
        <div class="hero-actions mt-8">
          <a href="translate.html" class="btn-primary hero-cta">Start Translating →</a>
          <div class="theme-pill" id="heroPill" style="align-self: center;">
            <button class="theme-pill-btn" id="heroLight" onclick="setTheme('light')">☀ Light</button>
            <button class="theme-pill-btn" id="heroDark"  onclick="setTheme('dark')">🌙 Dark</button>
          </div>
        </div>
      </section>

      <!-- Stats row -->
      <div class="stats-row" id="statsRow">
        <div class="stat-item" style="grid-column: 1 / -1;">
          <span class="stat-value" id="statTotal">—</span>
          <span class="stat-label">words, phrases, and proverbs ready to explore</span>
        </div>
      </div>
```

- [ ] **Step 2: Update the stats-fetch script to populate the combined total**

Locate the existing stats-fetch script (currently at the end of `frontend/index.html`, inside the final `<script>` block):

```javascript
// Load stats from /api/v1/knowledge/status
fetch('/api/v1/knowledge/status')
  .then(r => r.json())
  .then(d => {
    // CHANGED: Unpack d.collections to handle API response shape
    const c = d.collections ?? d;
    document.getElementById('statVocab').textContent     = (c.vocabulary ?? '—').toLocaleString();
    document.getElementById('statSentences').textContent = (c.sentences  ?? '—').toLocaleString();
    document.getElementById('statGrammar').textContent   = (c.grammar    ?? '—').toLocaleString();
    document.getElementById('statProverbs').textContent  = (c.proverbs   ?? '—').toLocaleString();
  })
  .catch(() => {});
```

Replace it with:

```javascript
// Load stats from /api/v1/knowledge/status — show one friendly combined total.
fetch('/api/v1/knowledge/status')
  .then(r => r.json())
  .then(d => {
    const c = d.collections ?? d;
    const total = Object.values(c).reduce((sum, n) => sum + (typeof n === 'number' ? n : 0), 0);
    document.getElementById('statTotal').textContent = total > 0 ? total.toLocaleString() : '—';
  })
  .catch(() => {});
```

- [ ] **Step 3: Confirm the grid CSS needs no further changes**

`frontend/styles.css:569-578` defines `.stats-row` as `display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));` (4 equal columns). The `grid-column: 1 / -1` added to the single remaining `.stat-item` in Step 1 makes it span the full row automatically — no CSS edit needed here, only the markup change from Step 1.

- [ ] **Step 4: Visual verification**

```bash
cd D:\projects\Luganda_AI_Studio
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open `http://127.0.0.1:8000/app/index.html`. Expected: hero shows "Verified by native Luganda speakers — works offline, no account needed to start." (not "built to run on your machine"), and below it a single centered stat showing something like "622 words, phrases, and proverbs ready to explore" — not 4 separate technical labels. No layout overflow or squishing.

- [ ] **Step 5: Commit**

```bash
git add frontend/index.html
git commit -m "feat: replace raw stat breakdown with friendly combined total on home hero"
```

---

## Task 5: Warmer Translate empty/error-state copy

**Files:**
- Modify: `frontend/translate.html:150-156`

Current markup (lines 150-156):

```html
          <!-- NOT FOUND -->
          <div id="stateNotFound" style="display:none;">
            <div style="font-size:14px;color:var(--warning,#d99b2a);line-height:1.65;" id="notFoundText">
              No translation found in the current dataset.
              The Luganda knowledge base is growing — try a simpler word,
              or use the Expected Output field below to record the correct answer.
            </div>
          </div>
```

- [ ] **Step 1: Confirm the exact current copy and surrounding context**

```bash
cd D:\projects\Luganda_AI_Studio
grep -n "stateNotFound\|notFoundText\|stateError\|errorText" -A 5 frontend/translate.html | head -20
```

- [ ] **Step 2: Rewrite the not-found copy**

Change:

```html
          <!-- NOT FOUND -->
          <div id="stateNotFound" style="display:none;">
            <div style="font-size:14px;color:var(--warning,#d99b2a);line-height:1.65;" id="notFoundText">
              No translation found in the current dataset.
              The Luganda knowledge base is growing — try a simpler word,
              or use the Expected Output field below to record the correct answer.
            </div>
          </div>
```

to:

```html
          <!-- NOT FOUND -->
          <div id="stateNotFound" style="display:none;">
            <div style="font-size:14px;color:var(--warning,#d99b2a);line-height:1.65;" id="notFoundText">
              We don't know this word yet — but you can teach us!
              Try a simpler word or phrase, or type the correct translation
              below and we'll add it to the dictionary for everyone.
            </div>
          </div>
```

- [ ] **Step 3: Rewrite the developer-facing fallback error message**

`frontend/translate.html:727-730` (inside the `catch` block of the translate fetch call) currently reads:

```javascript
  } catch (err) {
    if (err.name === 'TimeoutError' || err.name === 'AbortError') {
      showError('Request timed out. The server took too long to respond. Please try again.');
    } else {
      showError('Could not reach the translation API. Make sure the backend is running on port 8000.');
    }
```

The second message ("Make sure the backend is running on port 8000") is internal developer debugging language exposed to end users. Change it to:

```javascript
  } catch (err) {
    if (err.name === 'TimeoutError' || err.name === 'AbortError') {
      showError('Request timed out. The server took too long to respond. Please try again.');
    } else {
      showError('We couldn\'t reach the server. Check your connection and try again.');
    }
```

Leave the timeout message and the HTTP-status-derived message at line 700-701 (`data.detail || data.error || data.message || \`Server error (${response.status})\``) unchanged — those surface either a real backend-provided detail or a clearly-labelled status code, which is acceptable diagnostic information, not raw infra leakage like "port 8000."

- [ ] **Step 4: Manual verification**

```bash
cd D:\projects\Luganda_AI_Studio
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open `http://127.0.0.1:8000/app/translate.html`, type a nonsense string like `xyzabc123notaword` and click Translate.

Expected: the not-found message now reads "We don't know this word yet — but you can teach us! ..." instead of "No translation found in the current dataset."

- [ ] **Step 5: Verify the correction-save flow still works after the copy change**

Click "Wrong" on any translation result, type a correction in the Expected Output field, click Save Correction.

Expected: still succeeds (no regression from Phase 0's fix) — this only changed display copy, not any IDs or JS logic the feedback flow depends on.

- [ ] **Step 6: Commit**

```bash
git add frontend/translate.html
git commit -m "fix: warm up not-found and error copy on translate page"
```

---

## Final Verification (run after all tasks complete)

- [ ] Load `index.html` on a phone-width viewport: hero shows trust-line copy, single friendly stat total, streak pill shows `🔥 0` (or current count) in the topbar.
- [ ] Load `translate.html`: streak pill renders in topbar; translating a nonsense word shows the new warm not-found copy; Wrong→correction→Save Correction still works (Phase 0 regression check).
- [ ] Load `search.html`: streak pill renders in topbar (no other changes expected here this phase).
- [ ] Load `teach.html`: complete one full flash-card session → done-screen shows `🔥 Streak: 1 day · +N XP`; reload any page → topbar pill reflects the same count; running a second session same day does not double-increment; running a quiz session also shows the streak/XP line correctly.
- [ ] No console errors on any of the 4 pages (`streak.js` not found, `recordSessionComplete is not defined`, etc.) — open DevTools console on each page and confirm clean.
- [ ] All changes committed in 5 separate commits (Tasks 1–5), each independently buildable/revertable.

Once all boxes are checked, Phase 1 (this UX pass) is done. Resume the roadmap at Phase 2
(translation accuracy & data quality — gloss audit, search-ranking fix, dataset expansion) —
see `project_luganda_app_roadmap.md` memory and the master plan file for full Phase 2 scope.
The Search word-page redesign noted as deferred in the design spec should be revisited once
Phase 2's search-ranking fix lands, since a good word-page depends on good ranking underneath it.
