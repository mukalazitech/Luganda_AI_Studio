# Teach Flash Card — Category Cue + Bigger Cards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a per-word category emoji cue to Teach flash cards and make the cards fill most of the viewport.

**Architecture:** The vocabulary already carries a clean `category` per word in ChromaDB metadata; the API just drops it. Task 1 surfaces `category` through the `/api/v1/teach/cards` response. Task 2 extracts the category→emoji mapping into a standalone, testable JS module (mirroring the existing `mascot.js` pattern). Task 3 wires the module into `teach.html`. Task 4 enlarges the card via CSS only.

**Tech Stack:** FastAPI + Pydantic (backend), pytest + `TestClient` (backend tests), vanilla JS + `node:test` (frontend), plain CSS.

**Spec:** `docs/superpowers/specs/2026-06-24-teach-flashcard-category-cue-bigger-cards-design.md`

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `backend/api/routes/teach.py` | Add `category` to `FlashCard` model, loader, response, fallback cards | Modify |
| `tests/test_teach_route.py` | Assert `/cards` returns `category` | Create |
| `frontend/category-icons.js` | Pure category→emoji map + label formatter (dual export) | Create |
| `frontend/tests/category-icons.test.js` | Unit-test the mapping + formatter | Create |
| `frontend/teach.html` | Card-front emoji markup + wire module into `showFlashCard` | Modify |
| `frontend/styles.css` | Bigger card / word / emoji at all breakpoints | Modify |

---

## Task 1: Surface `category` through the flash-card API

**Files:**
- Modify: `backend/api/routes/teach.py` (`FlashCard` model ~61-66; `_load_vocabulary_from_chroma` ~198-207; `get_flash_cards` builder ~370-379; `FALLBACK_CARDS` ~123-139)
- Test: `tests/test_teach_route.py` (create)

- [ ] **Step 1: Write the failing test**

Create `tests/test_teach_route.py`:

```python
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_cards_response_includes_category_field():
    """Every flash card must expose a `category` field (may be empty string)."""
    res = client.get("/api/v1/teach/cards?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert data["cards"], "expected at least one card"
    for card in data["cards"]:
        assert "category" in card, "each card must include a 'category' key"
        assert isinstance(card["category"], str)


def test_fallback_animal_card_has_animals_category():
    """When ChromaDB is empty the fallback set is used; its animal rows
    must carry category='animals' so the UI shows the right icon.
    Embwa (Dog) is a fallback animal row."""
    res = client.get("/api/v1/teach/cards?limit=50&shuffle=false")
    assert res.status_code == 200
    cards = res.json()["cards"]
    embwa = next((c for c in cards if c["luganda"] == "Embwa"), None)
    # Only asserted when fallback data is in play (Embwa present).
    if embwa is not None:
        assert embwa["category"] == "animals"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_teach_route.py -v`
Expected: `test_cards_response_includes_category_field` FAILS with `KeyError`/assert on missing `'category'`.

- [ ] **Step 3: Add `category` to the `FlashCard` model**

In `backend/api/routes/teach.py`, change the model:

```python
class FlashCard(BaseModel):
    id:       str
    luganda:  str
    english:  str
    type:     str = "vocabulary"
    notes:    str = ""
    category: str = ""
```

- [ ] **Step 4: Populate `category` in the ChromaDB loader**

In `_load_vocabulary_from_chroma`, inside the per-entry loop, add a `category` read next to `notes`/`card_type` and include it in the appended dict:

```python
            notes    = str(meta.get("notes") or meta.get("example_sentence_english") or "")
            card_type = str(meta.get("data_type") or meta.get("_collection") or "vocabulary")
            category  = str(meta.get("category") or "").strip().lower()

            cards.append({
                "id":       entry_id,
                "luganda":  luganda,
                "english":  english,
                "type":     card_type,
                "notes":    notes,
                "category": category,
            })
```

- [ ] **Step 5: Add `category` to the fallback cards**

Replace the `FALLBACK_CARDS` list with category-tagged rows:

```python
FALLBACK_CARDS = [
    {"id": "f001", "luganda": "Oli otya",      "english": "How are you?",       "type": "greeting",   "notes": "Very common casual greeting",            "category": "greeting"},
    {"id": "f002", "luganda": "Bulungi",        "english": "Fine / Good",         "type": "greeting",   "notes": "Standard reply to 'Oli otya'",           "category": "greeting"},
    {"id": "f003", "luganda": "Webale nyo",     "english": "Thank you very much", "type": "greeting",   "notes": "'Webale' alone = 'thank you'",           "category": "greeting"},
    {"id": "f004", "luganda": "Amazzi",         "english": "Water",               "type": "vocabulary", "notes": "",                                       "category": "food_and_drink"},
    {"id": "f005", "luganda": "Emmere",         "english": "Food",                "type": "vocabulary", "notes": "Food in general",                        "category": "food_and_drink"},
    {"id": "f006", "luganda": "Ssebo",          "english": "Sir / Mr.",           "type": "vocabulary", "notes": "Respectful address for older man",        "category": "family"},
    {"id": "f007", "luganda": "Nnyabo",         "english": "Madam / Mrs.",        "type": "vocabulary", "notes": "Respectful address for older woman",      "category": "family"},
    {"id": "f008", "luganda": "Embwa",          "english": "Dog",                 "type": "vocabulary", "notes": "",                                       "category": "animals"},
    {"id": "f009", "luganda": "Embuzi",         "english": "Goat",                "type": "vocabulary", "notes": "",                                       "category": "animals"},
    {"id": "f010", "luganda": "Enkoko",         "english": "Hen / Chicken",       "type": "vocabulary", "notes": "",                                       "category": "animals"},
    {"id": "f011", "luganda": "Enjovu",         "english": "Elephant",            "type": "vocabulary", "notes": "",                                       "category": "animals"},
    {"id": "f012", "luganda": "Empologoma",     "english": "Lion",                "type": "vocabulary", "notes": "",                                       "category": "animals"},
    {"id": "f013", "luganda": "Erinnya lyange", "english": "My name is",          "type": "phrase",     "notes": "Follow with your name",                  "category": "greeting"},
    {"id": "f014", "luganda": "Nkwagala",       "english": "I love you",          "type": "phrase",     "notes": "Used between family and close friends",   "category": "emotions"},
    {"id": "f015", "luganda": "Mu kitiibwa",    "english": "You are welcome",     "type": "phrase",     "notes": "Response to 'webale'",                   "category": "greeting"},
]
```

- [ ] **Step 6: Include `category` when building the response**

In `get_flash_cards`, add `category` to the `FlashCard(...)` construction:

```python
    flash_cards = [
        FlashCard(
            id       = str(c.get("id", "")),
            luganda  = str(c.get("luganda", "")),
            english  = str(c.get("english", "")),
            type     = str(c.get("type", "vocabulary")),
            notes    = str(c.get("notes", "")),
            category = str(c.get("category", "")),
        )
        for c in selected
    ]
```

- [ ] **Step 7: Run test to verify it passes**

Run: `python -m pytest tests/test_teach_route.py -v`
Expected: both tests PASS.

- [ ] **Step 8: Commit**

```bash
git add backend/api/routes/teach.py tests/test_teach_route.py
git commit -m "feat(teach): surface word category in flash-card API"
```

---

## Task 2: Category-icon module (pure, testable)

**Files:**
- Create: `frontend/category-icons.js`
- Test: `frontend/tests/category-icons.test.js`

This mirrors the existing `frontend/mascot.js` dual-export pattern (CommonJS for
`node:test`, global for the browser).

- [ ] **Step 1: Write the failing test**

Create `frontend/tests/category-icons.test.js`:

```javascript
const test = require('node:test');
const assert = require('node:assert');
const { categoryIcon, categoryLabel, CATEGORY_ICON, FALLBACK_ICON } = require('../category-icons.js');

test('maps each known category to its emoji', () => {
  assert.strictEqual(categoryIcon('animals'), '🐐');
  assert.strictEqual(categoryIcon('food_and_drink'), '🍲');
  assert.strictEqual(categoryIcon('colors'), '🎨');
});

test('is case-insensitive and trims input', () => {
  assert.strictEqual(categoryIcon('  ANIMALS '), '🐐');
});

test('falls back for unknown or empty category', () => {
  assert.strictEqual(categoryIcon('zzz'), FALLBACK_ICON);
  assert.strictEqual(categoryIcon(''), FALLBACK_ICON);
  assert.strictEqual(categoryIcon(null), FALLBACK_ICON);
  assert.strictEqual(categoryIcon(undefined), FALLBACK_ICON);
});

test('formats labels: underscores to spaces, _and_ to &, capitalised', () => {
  assert.strictEqual(categoryLabel('food_and_drink'), 'Food & drink');
  assert.strictEqual(categoryLabel('body_parts'), 'Body parts');
  assert.strictEqual(categoryLabel('animals'), 'Animals');
});

test('every category in the map also formats to a non-empty label', () => {
  for (const cat of Object.keys(CATEGORY_ICON)) {
    assert.ok(categoryLabel(cat).length > 0, `${cat} must format to a label`);
  }
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test frontend/tests/category-icons.test.js`
Expected: FAIL — `Cannot find module '../category-icons.js'`.

- [ ] **Step 3: Write the module**

Create `frontend/category-icons.js`:

```javascript
/* category-icons.js — maps a word's semantic category to an emoji cue.
   The 12 categories come from datasets/vocabulary/*.json plus 'greeting'
   from the API fallback set. One emoji per category scales to every word. */

const CATEGORY_ICON = {
  animals:        '🐐',
  food_and_drink: '🍲',
  family:         '👪',
  body_parts:     '✋',
  transport:      '🚲',
  numbers:        '🔢',
  time:           '⏰',
  health:         '❤️‍🩹',
  places:         '🏠',
  clothing:       '👕',
  emotions:       '😊',
  colors:         '🎨',
  greeting:       '👋',
};

const FALLBACK_ICON = '📖';

function categoryIcon(category) {
  if (!category || typeof category !== 'string') return FALLBACK_ICON;
  return CATEGORY_ICON[category.trim().toLowerCase()] || FALLBACK_ICON;
}

function categoryLabel(category) {
  if (!category || typeof category !== 'string') return '';
  const words = category.trim().toLowerCase().replace(/_and_/g, ' & ').replace(/_/g, ' ');
  return words.charAt(0).toUpperCase() + words.slice(1);
}

// Dual export: CommonJS for node:test, global for the browser (matches mascot.js).
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { categoryIcon, categoryLabel, CATEGORY_ICON, FALLBACK_ICON };
}
if (typeof window !== 'undefined') {
  window.categoryIcon = categoryIcon;
  window.categoryLabel = categoryLabel;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test frontend/tests/category-icons.test.js`
Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/category-icons.js frontend/tests/category-icons.test.js
git commit -m "feat(teach): category-to-emoji mapping module"
```

---

## Task 3: Render the emoji cue on the flash card

**Files:**
- Modify: `frontend/teach.html` (head script tags ~20-21; `.card-front` markup ~142-148; `showFlashCard` ~297-312)

- [ ] **Step 1: Load the module in `<head>`**

In `frontend/teach.html`, after the `mascot.js` script tag (line ~21), add:

```html
  <script src="/app/category-icons.js"></script>
```

- [ ] **Step 2: Add the emoji element to the card front**

In the `.card-front` block, insert the emoji **above** `#cardLuganda`. The block becomes:

```html
            <div class="card-face card-front">
              <div class="card-badge">Luganda</div>
              <div class="card-emoji" id="cardEmoji" aria-hidden="true">📖</div>
              <div class="card-word" id="cardLuganda">—</div>
              <button class="tts-btn" id="ttsBtnCard" style="display:none" title="Speak Luganda" aria-label="Listen to Luganda">🔊 Listen</button>
              <div class="card-hint">Tap card to reveal the meaning</div>
              <div class="card-type-tag" id="cardType">vocabulary</div>
            </div>
```

- [ ] **Step 3: Set the emoji + category label in `showFlashCard`**

In `showFlashCard(index)`, replace the line that sets `#cardType`:

```javascript
  document.getElementById('cardType').textContent    = card.type    || 'vocabulary';
```

with the category-aware version:

```javascript
  const cat = (card.category || '').toLowerCase();
  document.getElementById('cardEmoji').textContent = window.categoryIcon(cat);
  document.getElementById('cardType').textContent  = cat
    ? window.categoryLabel(cat)
    : (card.type || 'vocabulary');
```

- [ ] **Step 4: Verify in the browser**

Run the app (`python -m backend.main` or the project's run command) and open the Teach page.
Expected: each card front shows a large emoji above the Luganda word, and the
top-right chip shows a readable category (e.g. "Animals", "Food & drink"). With
ChromaDB empty, the fallback animal cards (Embwa, Embuzi…) show 🐐 + "Animals".

- [ ] **Step 5: Commit**

```bash
git add frontend/teach.html
git commit -m "feat(teach): show category emoji cue on flash card front"
```

---

## Task 4: Make the flash card fill the viewport

**Files:**
- Modify: `frontend/styles.css` (`.flash-card` ~953-959; `.card-word` ~992; add `.card-emoji`; `@media (max-width:768px)` ~1114-1124; `@media (max-width:480px)` ~1126-1133)

CSS only — no unit test; verify visually at three widths.

- [ ] **Step 1: Enlarge the card and word (desktop)**

In `frontend/styles.css`, change `.flash-card` min-height:

```css
.flash-card {
  width: 100%; min-height: min(68vh, 480px);
  position: relative; cursor: pointer;
  transform-style: preserve-3d;
  transition: transform 0.5s cubic-bezier(0.4,0,0.2,1);
  border-radius: var(--radius-lg);
}
```

Change `.card-word`:

```css
.card-word { font-family: var(--font-display); font-size: 52px; font-weight: 700; color: var(--text-primary); line-height: 1.2; margin-bottom: 12px; }
```

- [ ] **Step 2: Add the `.card-emoji` rule**

Immediately after the `.card-word` rule, add:

```css
.card-emoji { font-size: 60px; line-height: 1; margin-bottom: 16px; }
```

- [ ] **Step 3: Scale down at the 768px breakpoint**

In the `@media (max-width: 768px)` block, update `.card-word` and add `.card-emoji`:

```css
@media (max-width: 768px) {
  .card-word    { font-size: 40px; }
  .card-emoji   { font-size: 52px; margin-bottom: 12px; }
  .quiz-word    { font-size: 28px; }
  /* CHANGED: quiz options — single column on mobile for readability */
  .quiz-options { grid-template-columns: 1fr; gap: 10px; }
  .quiz-option  { min-height: 52px; font-size: 15px; }
  .mode-btn     { min-height: 44px; padding: 8px 14px; font-size: 13px; }
  /* CHANGED: flash card padding tighter on small screens */
  .card-face    { padding: 24px 20px; }
  .quiz-card    { padding: 24px 20px; }
}
```

- [ ] **Step 4: Scale at the 480px breakpoint (covers 390px)**

In the `@media (max-width: 480px)` block, update `.card-word` and add `.card-emoji`:

```css
@media (max-width: 480px) {
  .card-word  { font-size: 38px; }
  .card-emoji { font-size: 48px; margin-bottom: 10px; }
  .quiz-word  { font-size: 24px; }
  .done-score { font-size: 40px; }
  /* CHANGED: done-stats stacks vertically on tiny phones */
  .done-stats { flex-direction: column; align-items: center; gap: 10px; }
  .done-stat  { min-width: 140px; }
}
```

- [ ] **Step 5: Verify at three widths**

Open Teach in the browser and check at desktop, 768px, and 390px (DevTools device toolbar):
- Card fills most of the viewport; the Luganda word is the visual hero.
- Emoji is clearly visible above the word.
- Progress bar (top) and Got It / Try Again buttons (below) remain visible and usable on a 390px-wide phone — the card does not push the answer row off-screen.

- [ ] **Step 6: Commit**

```bash
git add frontend/styles.css
git commit -m "feat(teach): enlarge flash card to fill viewport"
```

---

## Self-Review Notes

- **Spec coverage:** §4A backend → Task 1; §4A frontend map → Task 2; §4A markup/render → Task 3; §4B bigger cards → Task 4. Acceptance criteria 1–6 all map to a task (1→T1, 2→T3, 3→T3, 4→T2/T3, 5→T4, 6→untouched by scope).
- **Out of scope respected:** quiz card, flip, TTS, mic, ingestion — none touched.
- **Type consistency:** `category` (str) is the single field name across model, loader, fallback, response, and the frontend `card.category` read. `categoryIcon`/`categoryLabel` names match between module, test, and `teach.html` usage.
- **No placeholders:** every code step shows complete code; every run step shows the command and expected result.
