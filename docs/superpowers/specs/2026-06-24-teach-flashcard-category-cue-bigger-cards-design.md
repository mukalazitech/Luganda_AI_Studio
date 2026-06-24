# Teach Flash Cards — Category Visual Cue + Bigger Cards

**Date:** 2026-06-24
**App:** Luganda AI Studio
**Scope:** `frontend/teach.html`, `frontend/styles.css`, `backend/api/routes/teach.py`
**Status:** Approved design — ready for implementation plan

---

## 1. Problem

The Teach flash-card flow shows only the Luganda word, English meaning, and an
example sentence. Two gaps:

1. **No visual meaning cue.** A learner sees text only. There is nothing that
   represents a word's meaning at a glance to prime recall.
2. **Cards are small.** `.flash-card` is `min-height: 260px` and the word is
   `36px` (24px on mobile). The card competes with page chrome (header,
   subtitle, mode toggle) instead of dominating the screen, so the learner
   cannot focus on one word at a time.

---

## 2. Key finding that shaped the design

The vocabulary is **already organised into 12 clean, human-curated categories**
in `datasets/vocabulary/*.json` (~424 entries total):

| Category | Entries | Category | Entries |
|---|---|---|---|
| food_and_drink | 56 | family | 38 |
| animals | 54 | time | 30 |
| body_parts | 50 | health | 25 |
| transport | 49 | places | 22 |
| numbers | 47 | clothing | 20 |
| | | emotions | 18 |
| | | colors | 15 |

Each entry carries a clean `category` value (matching its filename) plus a
`subcategory`. ChromaDB metadata already stores `category`
(`backend/services/ingestion/loader.py:199, 237`). The loader already reads it.

**The catch:** the flash-card API (`backend/api/routes/teach.py`) *drops*
`category` at the response boundary. The `FlashCard` model exposes only
`luganda / english / type / notes`, where `type` is ingestion provenance
(`data_type` = "vocabulary" / "sentence" / "grammar"), **not** a semantic
category. So the front end has no category to display today even though the
data has one.

This is why **category icons** are the right cue (not emoji-per-word or
per-word illustrations): the per-word category mapping already exists in the
data, so 12 icons cover the entire vocabulary — and every future word — with
zero per-word tagging.

---

## 3. Decisions (locked with user)

| Decision | Choice |
|---|---|
| Cue type | **Category icon**, one per category (not emoji-per-word, not per-word art) |
| Glyph style | **Emoji glyphs** — zero assets, offline, renders on every phone, ships today |
| Backend | **Yes** — surface `category` from the API (loader already reads it) |
| Emoji placement | **Above** the Luganda word on the card **front** (emoji on top, big word below) |
| "Fill the viewport" | Card **dominates** the space; progress bar + answer buttons stay (functional) — not literally edge-to-edge full-screen |

---

## 4. Design

### 4A. Category visual cue (emoji)

**Backend — `backend/api/routes/teach.py`**

1. Add a field to the response model:
   ```python
   class FlashCard(BaseModel):
       id:       str
       luganda:  str
       english:  str
       type:     str = "vocabulary"
       notes:    str = ""
       category: str = ""        # NEW — semantic category (animals, food_and_drink, ...)
   ```
2. Populate `category` in `_load_vocabulary_from_chroma()` from
   `meta.get("category")` (already in metadata), defaulting to `""`.
3. Include `category` when building `FlashCard` in `get_flash_cards()`.
4. Add `category` to the `FALLBACK_CARDS` dicts so the fallback set also gets
   sensible icons. Concrete mapping: the greeting/phrase rows → `"greeting"`;
   the animal rows (Embwa, Embuzi, Enkoko, Enjovu, Empologoma) → `"animals"`;
   the food/water rows (Amazzi, Emmere) → `"food_and_drink"`; the rest → `""`
   (renders the `📖` fallback).

Backward-compatible: default `""`, no breaking change to existing callers.

**Frontend — `frontend/teach.html`**

5. Add a `CATEGORY_ICON` map (single source of truth, 12 + fallback):

   ```js
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
     greeting:       '👋',   // from fallback data
   };
   const FALLBACK_ICON = '📖';
   ```

   A small helper formats the label for display
   (`food_and_drink` → `Food & drink`, `body_parts` → `Body parts`).

6. Add markup to the **card front** (`.card-front`), above `#cardLuganda`:
   ```html
   <div class="card-emoji" id="cardEmoji" aria-hidden="true">📖</div>
   ```
   Repurpose the existing `.card-type-tag` (`#cardType`, top-right, currently
   shows "vocabulary") to show the **category label** instead.

7. In `showFlashCard(index)`:
   ```js
   const cat  = (card.category || '').toLowerCase();
   const icon = CATEGORY_ICON[cat] || FALLBACK_ICON;
   document.getElementById('cardEmoji').textContent = icon;
   document.getElementById('cardType').textContent  = cat ? formatCategory(cat) : (card.type || 'vocabulary');
   ```
   The emoji lives on the **front** (with the Luganda word, before flip) — that
   is where the meaning cue helps recall. The back keeps English + notes
   unchanged.

**Accessibility:** the emoji is `aria-hidden="true"` (decorative — the category
chip carries the readable label).

### 4B. Bigger cards

All changes are CSS in `frontend/styles.css`, scoped to the flash card.

| Element | Now | Target |
|---|---|---|
| `.flash-card` min-height | `260px` | `min(68vh, 480px)` desktop |
| `.card-word` | `36px` | `~52px` desktop |
| `.card-emoji` | — | `~60px` (new) |
| Mobile `≤768px` `.card-word` | `28px` | `~40px` |
| Mobile `≤480px` `.card-word` (390px target) | `24px` | `~38px` |
| Mobile `.card-emoji` | — | `~48px` |
| `.card-face` padding (mobile) | `24px 20px` | keep tight; let height come from min-height |

- The **card dominates** the space between the progress bar (kept) and the
  Got It / Try Again row (kept). Both are functional and stay visible.
- **Less chrome on the teach page only:** tighten the page header/subtitle
  spacing so the card breathes. Do **not** remove the progress bar, answer
  buttons, skip/mic row, or mode toggle.
- On mobile, `min-height` is viewport-driven so one word fills most of the
  screen without the card running off-screen or pushing the answer buttons
  below the fold on a 390px-wide phone.

Verify at: desktop, `768px` breakpoint, `480px`/`390px` breakpoint.

---

## 5. Out of scope (YAGNI)

- Quiz card (`.quiz-card`, quiz word, options) — untouched.
- Flip animation, TTS, mic/STT logic — untouched.
- Data ingestion / dataset files — untouched (only *reading* `category`).
- Per-word emoji overrides / hybrid cue — possible later; not v1.
- Subcategory display — `category` is enough for v1.

---

## 6. Acceptance criteria

1. `/api/v1/teach/cards` response includes a `category` field per card.
2. Each flash card front shows a large category emoji above the Luganda word.
3. The top-right chip shows a readable category label (e.g. "Animals",
   "Food & drink") for categorised words; falls back gracefully for
   uncategorised ones (`📖` + the existing type).
4. All 12 categories map to a distinct emoji; uncategorised words show the
   fallback `📖` and never a blank.
5. The flash card fills most of the viewport on desktop, 768px, and 390px,
   with a noticeably larger word; progress bar and answer buttons remain
   visible and usable.
6. Quiz mode, flip, TTS, and mic are unchanged.
