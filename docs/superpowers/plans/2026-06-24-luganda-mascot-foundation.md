# Mascot Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the reusable mascot personality layer (`mascot.js`) and prove it end-to-end by showing Kintu in his `cheering` state on the Home page — using the existing grinning-boy artwork, so this ships without waiting on any new art.

**Architecture:** A small dependency-free script mirrors `streak.js` conventions: plain global functions, loaded via `<script src="/app/mascot.js">`, declarative auto-init that scans for `.mascot-slot[data-character]` elements and renders them, and safe no-ops when a slot is absent. Pure path-resolution logic is split from DOM side-effects so it can be unit-tested in Node; visual behaviour is verified live in the browser (the established pattern for this frontend). Image files live under `frontend/assets/characters/<character>/<state>.png` and are served at `/app/assets/...` by the existing static mount.

**Tech Stack:** Vanilla JS (no framework), HTML, CSS custom properties, Node 24 built-in test runner (`node --test`), ffmpeg (already on PATH) for image optimization, Chrome DevTools MCP for live verification.

**Spec:** `docs/superpowers/specs/2026-06-24-luganda-two-character-pilot-design.md`

> **Before starting:** create an isolated branch/worktree per the established phase workflow (superpowers:using-git-worktrees). Do NOT work directly on `master`. The repo has uncommitted ChromaDB runtime binaries — **every commit step below stages explicit paths only; never `git add -A`.**

---

## File Structure

- **Create** `frontend/mascot.js` — the mascot module. Responsibilities: resolve character+state → image path (`mascotSrc`), swap the image in a slot (`setMascot`), declarative auto-init (`initMascots`). One file, three small functions.
- **Create** `frontend/tests/mascot.test.js` — Node unit tests for the pure `mascotSrc` logic.
- **Create** `frontend/assets/characters/kintu/cheering.png` — Kintu's first state, optimized from the existing grinning-boy source image.
- **Modify** `frontend/styles.css` — add `.mascot-slot` + `.mascot-img` rules (append at end).
- **Modify** `frontend/index.html` — add the Kintu mascot slot in the hero (after line 75) and the `mascot.js` script include (after line 20).

---

## Task 1: Create Kintu's `cheering` artwork from the existing image

**Files:**
- Create: `frontend/assets/characters/kintu/cheering.png`
- Source: `assets/characters/A5243686-A2F1-427F-8490-FAD9DFC3F100.PNG` (repo-root, the grinning "ROAARR" boy)

- [ ] **Step 1: Create the directory and optimized image**

Run (from repo root `D:/projects/Luganda_AI_Studio`):

```bash
mkdir -p frontend/assets/characters/kintu
ffmpeg -y -loglevel error \
  -i "assets/characters/A5243686-A2F1-427F-8490-FAD9DFC3F100.PNG" \
  -vf "scale=300:-1" \
  frontend/assets/characters/kintu/cheering.png
```

- [ ] **Step 2: Verify the file exists and is web-sized**

Run:

```bash
ls -la frontend/assets/characters/kintu/cheering.png
```

Expected: file exists, width 300px, size under ~200 KB. (This is a real first state — the cream paper background is acceptable for the pilot; a transparent regenerated version comes later from Patrick's art pipeline.)

- [ ] **Step 3: Commit**

```bash
git add frontend/assets/characters/kintu/cheering.png
git commit -m "feat(mascot): add Kintu cheering state from existing artwork"
```

---

## Task 2: Write the failing test for `mascotSrc`

**Files:**
- Create: `frontend/tests/mascot.test.js`

- [ ] **Step 1: Write the failing test**

Create `frontend/tests/mascot.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert');
const { mascotSrc, MASCOT_STATES, MASCOT_BASE } = require('../mascot.js');

test('resolves a valid character+state to its image path', () => {
  assert.strictEqual(mascotSrc('kintu', 'celebrate'), `${MASCOT_BASE}/kintu/celebrate.png`);
  assert.strictEqual(mascotSrc('nambi', 'explaining'), `${MASCOT_BASE}/nambi/explaining.png`);
});

test('falls back to the character default state when state is unknown', () => {
  // kintu default = first listed state = 'cheering'
  assert.strictEqual(mascotSrc('kintu', 'no-such-state'), `${MASCOT_BASE}/kintu/cheering.png`);
  // nambi default = 'neutral'
  assert.strictEqual(mascotSrc('nambi', 'bogus'), `${MASCOT_BASE}/nambi/neutral.png`);
});

test('returns null for an unknown character so callers can no-op', () => {
  assert.strictEqual(mascotSrc('zzz', 'cheering'), null);
});

test('every character has at least one state (the default)', () => {
  for (const [char, states] of Object.entries(MASCOT_STATES)) {
    assert.ok(Array.isArray(states) && states.length > 0, `${char} must list states`);
  }
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run (from repo root):

```bash
node --test frontend/tests/mascot.test.js
```

Expected: FAIL — `Cannot find module '../mascot.js'` (the module does not exist yet).

---

## Task 3: Implement `mascot.js`

**Files:**
- Create: `frontend/mascot.js`

- [ ] **Step 1: Write the implementation**

Create `frontend/mascot.js`:

```js
// frontend/mascot.js
// Mascot personality layer for Luganda AI Studio.
// State-based PNG swap — no framework, no rigging. Mirrors streak.js conventions:
// plain global functions, declarative auto-init on DOMContentLoaded, no-op when a
// slot is absent. Served at /app/mascot.js by the existing static mount.

const MASCOT_BASE = '/app/assets/characters';

// Known characters → valid states. FIRST state listed is the default/fallback.
const MASCOT_STATES = {
  kintu: ['cheering', 'happy', 'celebrate', 'oops', 'thinking'],
  nambi: ['neutral', 'explaining', 'challenging', 'impressed'],
};

// Pure: resolve a character+state to an image path. Falls back to the character's
// default (first) state when the state is unknown, so a typo never yields a 404 <img>.
// Returns null for an unknown character (caller no-ops).
function mascotSrc(character, state) {
  const states = MASCOT_STATES[character];
  if (!states) return null;
  const valid = states.includes(state) ? state : states[0];
  return `${MASCOT_BASE}/${character}/${valid}.png`;
}

// DOM: swap the <img> inside a mascot slot (a container element with the given id).
// Safe no-op when the slot is missing or the character is unknown.
function setMascot(slotId, character, state) {
  if (typeof document === 'undefined') return;
  const slot = document.getElementById(slotId);
  if (!slot) return;
  const src = mascotSrc(character, state);
  if (!src) return;
  let img = slot.querySelector('img');
  if (!img) {
    img = document.createElement('img');
    img.className = 'mascot-img';
    img.loading = 'lazy';
    slot.appendChild(img);
  }
  img.src = src;
  img.alt = `${character} mascot`;
  slot.dataset.character = character;
  slot.dataset.state = state;
}

// Declarative auto-init: render every <div class="mascot-slot" data-character="..."
// data-state="..."> on the page. Pages just drop the markup — no per-page script.
function initMascots() {
  if (typeof document === 'undefined') return;
  document.querySelectorAll('.mascot-slot[data-character]').forEach((slot) => {
    setMascot(slot.id, slot.dataset.character, slot.dataset.state || '');
  });
}

if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', initMascots);
}

// Node-testability — no effect in the browser, where `module` is undefined.
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { mascotSrc, setMascot, initMascots, MASCOT_STATES, MASCOT_BASE };
}
```

- [ ] **Step 2: Run the test to verify it passes**

Run (from repo root):

```bash
node --test frontend/tests/mascot.test.js
```

Expected: PASS — all 4 tests pass, 0 failures.

- [ ] **Step 3: Commit**

```bash
git add frontend/mascot.js frontend/tests/mascot.test.js
git commit -m "feat(mascot): add mascot.js state-swap module with unit tests"
```

---

## Task 4: Add mascot CSS

**Files:**
- Modify: `frontend/styles.css` (append at end of file)

- [ ] **Step 1: Append the mascot styles**

Add to the end of `frontend/styles.css`:

```css
/* ── Mascot layer ───────────────────────────────────────────── */
.mascot-slot {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  margin: 8px 0 0;
  pointer-events: none; /* never block taps on low-end mobile */
}
.mascot-img {
  width: 140px;
  max-width: 40vw;
  height: auto;
  border-radius: 14px;
  display: block;
}
@media (min-width: 900px) {
  .mascot-img { width: 170px; }
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/styles.css
git commit -m "feat(mascot): add mascot slot/image styles"
```

---

## Task 5: Add Kintu to the Home page

**Files:**
- Modify: `frontend/index.html` (script include after line 20; slot after line 75)

- [ ] **Step 1: Add the mascot.js script include**

In `frontend/index.html`, immediately after the existing streak.js include (line 20):

```html
  <script src="/app/streak.js"></script>
  <script src="/app/mascot.js"></script>
```

- [ ] **Step 2: Add the mascot slot to the hero**

In `frontend/index.html`, immediately after the closing `</section>` of the hero (currently line 75), insert:

```html
      </section>

      <!-- Kintu mascot (declarative — mascot.js auto-renders on load) -->
      <div id="homeMascot" class="mascot-slot" data-character="kintu" data-state="cheering"></div>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/index.html
git commit -m "feat(mascot): show Kintu cheering on the Home page"
```

---

## Task 6: Live verification

**Files:** none (verification only)

- [ ] **Step 1: Run the app**

Use the project's normal run method (the `/run` skill, or the backend that serves the frontend under `/app/`). The Home page must be reachable at `http://localhost:<port>/app/index.html`. Confirm the port before continuing.

- [ ] **Step 2: Verify in the browser via Chrome DevTools MCP**

- Navigate to `http://localhost:<port>/app/index.html`.
- Take a snapshot/screenshot. Expected: the Kintu grinning-boy image renders below the hero headline.
- List network requests; confirm `GET /app/assets/characters/kintu/cheering.png` returns **200** (not 404).
- List console messages; expected: **no errors** (mascot.js loaded, no ReferenceError).
- Resize to mobile width (~390px). Expected: image scales down (`max-width:40vw`), does not overflow or block the "Start Translating" button.

- [ ] **Step 3: Verify dark mode**

Toggle dark theme on the Home page. Expected: the mascot image still renders correctly (no broken layout). Note any visual issue for a later polish pass — do not block on it.

---

## Task 7: Wrap up

- [ ] **Step 1: Run the full frontend test once more**

```bash
node --test frontend/tests/mascot.test.js
```

Expected: PASS, 0 failures.

- [ ] **Step 2: Confirm clean git state (only intended files changed)**

```bash
git status --short
```

Expected: no unexpected staged files; the ChromaDB runtime binaries remain unstaged (never commit them here).

- [ ] **Step 3: Finish the branch**

Use superpowers:finishing-a-development-branch to merge to `master` (local merge, no PR — matches prior Luganda phases), then deploy per `project_luganda_app_railway` (`railway up --service Luganda_AI_Studio`) and re-verify Kintu renders on the live site.

---

## Self-review notes

- **Spec coverage:** This plan implements the spec's §7 technical foundation (`mascot.js` + slots + declarative init) and the first of §4's states (Kintu `cheering`) on the §5 Home placement. It deliberately does NOT cover Translate/Teach/Grammar/Proverbs/Search wiring or the remaining 8 states — those are follow-up plans gated on Patrick generating art from the spec's Appendix A prompts.
- **Type consistency:** `mascotSrc`, `setMascot`, `initMascots`, `MASCOT_STATES`, `MASCOT_BASE` are used identically in the module, its tests, and the Home markup (`data-character="kintu"`, `data-state="cheering"` match `MASCOT_STATES.kintu[0]`).
- **No placeholders:** every step has exact commands, code, and expected output.

## Follow-up plans (NOT in this plan)

1. **Kintu reactions in Translate** (the correction engine) — needs Kintu `happy`/`thinking`/`celebrate`/`oops`; wires into `runTranslation()`/`setFeedback()`/`submitWithExpected()`, rewards corrections with XP, and hides developer metadata from users.
2. **Teach with Nambi + Kintu** — needs Nambi's 4 states; wires the quiz flow.
3. **Grammar / Proverbs / Search touches.**

Each follows the same generate-art → wire → verify-live loop.
