# Luganda AI Studio — Two-Character Mascot Pilot (Design)

**Date:** 2026-06-24
**Status:** Approved direction (Style A), pending spec review → implementation plan
**Owner:** Patrick Mukalazi
**Related:** Phase 1 UX (`2026-06-23-luganda-app-phase1-ux-design.md`), the 5-phase roadmap, and the
correction-collection / Phase-4 LoRA goal (the app barely generates real correction signal today —
mascots + gamified corrections are the engine to fix that).

---

## 1. Goal

Give the app a **personality layer** that (a) makes it feel alive and distinctively African, and
(b) turns the existing translate/teach flows into a low-friction, *rewarded* way to collect user
corrections — the training signal we need and currently don't have.

This is a **deliberate small pilot: two characters only.** We ship two, watch how users respond,
then decide how many more to add and which content they should cover. We are NOT building a full
cast, hearts/energy, leagues, mini-games, or monetization in this pilot.

Grounded in competitive research (NKENNE, Duolingo, Busuu, uTalk, Memrise, Dialogue Africa) which
concluded: for a solo African-language founder, the highest-ROI move is a simple streak/XP loop +
**one host/guide character + one emotional sidekick**, soft (never hard-paywall) mechanics, and
local mobile-money pricing later.

---

## 2. Art style decision

- **NOW — Style A: hand-drawn ink-sketch "storybook."** Uses the look of Patrick's existing
  characters. Distinctive (no competitor looks like this — they're all glossy 3D or flat vector),
  warm, authentically African, and cheapest because we already own usable assets.
- **FUTURE — Style B: 3D claymation** (the NKENNE look Patrick screenshotted). Documented as a
  planned future upgrade, NOT in this pilot. When the loop is proven, the same characters can be
  re-rendered in 3D without changing the app logic (the mascot system is style-agnostic — it just
  swaps image files).

**Hard rule:** both characters must share ONE consistent style, framing, palette, and lighting so
they read as belonging to the same app.

---

## 3. The cast (two kids, both transformed from existing images)

All 7 of Patrick's source images are children; none is an elder. Decision: the pilot uses the two
**ink-sketch** kids (the only two assets with real character/personality and a matching style).
The photorealistic photos are NOT used as mascots (can't generate emotional states from a photo;
real-child-likeness/consent concerns). An elder "Jajja" character is deferred to a later phase.

| Character | Source image | Role | Personality |
|---|---|---|---|
| **Kintu** | `A5243686-…` grinning "ROAARR" dino-shirt boy | **Emotional Sidekick** | Warm, excitable, encouraging. The learner's friend. |
| **Nambi** | `AEBD4AE3-…` sassy girl with twists | **Guide / Quizmaster** | Confident, a little cheeky. Sets up lessons, runs quizzes, frames culture. |

(Names: **Kintu and Nambi** — the first man and woman in Buganda creation mythology. Culturally
resonant anchors for a Luganda heritage app.)

---

## 4. Emotional states (state-based PNG swaps — no rigging)

Each state is one transparent-background PNG, produced by **image-to-image transformation of the
single source image** (keep identity, change expression/pose). Fixed waist-up framing.

**Kintu (Sidekick) — 5 states**
- `cheering` — default / home / idle (thumbs up, big grin)
- `happy` — correct answer (smile, small nod)
- `celebrate` — streak kept / level complete (arms up, confetti-ready)
- `oops` — wrong answer / struggling (sheepish, hand on head) — also reused for "hearts low" later
- `thinking` — loading / waiting for translation

**Nambi (Guide/Quizmaster) — 4 states**
- `neutral` — friendly intro (sass dialed down, open posture)
- `explaining` — presenting a rule/proverb (pointing / gesturing)
- `challenging` — quiz mode (hands on hips, "can you get this?")
- `impressed` — you nailed it (approving, eyebrow raise)

Total pilot art = **9 PNGs**. Small, achievable, transformed from 2 source images.

---

## 5. Placement map (where each appears)

| Screen / section | Character + state behaviour |
|---|---|
| **Onboarding** | Nambi `neutral` welcomes ("Learn Luganda for family, market, church"); Kintu `cheering` beside her. |
| **Home** | Kintu `cheering` next to the 🔥 streak pill; switches to `celebrate` if today's streak is fresh. |
| **Translate** | Kintu `thinking` while translating → `happy` on a result. On 👍 it `celebrate`s; on 🤔 ("not quite") Kintu runs the rewarded "What should it be?" correction → on save, `celebrate` + XP. **This is the card-stack correction flow + the data-collection engine, unified.** |
| **Teach (flashcards/quiz)** | Nambi hosts the topic intro (`explaining`) and quiz prompts (`challenging`); Kintu reacts per answer (`happy`/`oops`); both `celebrate`/`impressed` on session complete. Reuses existing `streak.js` + XP. |
| **Grammar** | Nambi `explaining` frames each rule. |
| **Proverbs** | Nambi `explaining` gives the cultural meaning; Kintu adds a playful `happy`/`oops` reaction to the proverb's lesson. |
| **Search** | Light touch — Kintu `oops` only on the empty "we don't know this word yet" state, with a "teach us" nudge. |

---

## 6. Production pipeline (Patrick generates, Claude wires)

**Division of labour:** Claude writes the image-gen prompts + model sheets; **Patrick generates the
PNGs by transforming his existing images** in his own image tool; Claude integrates them.

1. **Model sheet per character** (Claude provides): locked description — skin tone, hair, clothing,
   eye shape, line-weight, paper/background treatment — so every generated state stays on-model.
2. **Image-to-image prompts** (Claude provides, one per state): "using THIS image as the character,
   keep the same face/hair/shirt/line-style, change to <pose/expression>, transparent background,
   waist-up." 9 prompts total (5 Kintu + 4 Nambi). Draft set in Appendix A.
3. **Consistency rules:** fixed waist-up framing, same palette/lighting, transparent PNG, same
   output resolution. No outfit changes between states (Duolingo's outfit experiments added cost
   for no learning benefit and were rolled back).
4. **Hand-off format:** Patrick drops finished PNGs into
   `frontend/assets/characters/{kintu,nambi}/<state>.png`. Claude wires them in.

---

## 7. Technical integration

- **New file `frontend/mascot.js`** — a tiny, dependency-free module exposing
  `setMascot(slot, character, state)` that swaps the `<img>` in a mascot slot. Pure PNG swap for
  the pilot; optional CSS micro-animation (blink/bounce) is a later polish, not required to ship.
- **Mascot slots** = a small reusable markup block dropped into each page's existing layout (Home,
  Translate, Teach, Search), positioned so it never blocks input on low-end mobile.
- **Event hooks** wire existing app events to mascot states: translation start/success, 👍/🤔
  feedback, correction saved, quiz answer correct/wrong, session complete, streak increment. Most
  of these call sites already exist (e.g. `finishSession()` in teach.html, `runTranslation()` /
  `setFeedback()` / `submitWithExpected()` in translate.html) — we add `setMascot(...)` calls, we
  do not rebuild the flows.
- **Reuse, don't rebuild:** streak/XP already exists in `streak.js` + teach.html; the correction
  POST already exists (`FEEDBACK_URL`). The pilot adds personality + reward feedback on top of
  working plumbing.
- **Asset weight:** ink PNGs must be exported web-optimized (target < ~80 KB each) and lazy-loaded —
  the audience is on low-end Android and personal data bundles.

---

## 8. Gamified data-collection tie-in (why this matters)

The real blocker for Phase 4 (LoRA fine-tune) is that the live app barely generates correction
signal — ~26 verified pairs, mostly Patrick's own testing, vs ~500 needed. This pilot directly
attacks that:

- Every wrong translation becomes an **easy, rewarded** "teach us" moment (Kintu celebrates + XP),
  instead of today's friction-heavy "Rate → Expected Output → disabled Save" developer UI.
- The dense developer metadata currently shown to users (confidence %, match_type chips,
  matched_collection, session stats, Export JSON) is **hidden from the normal user view** — it
  reads like a QA tool today, which suppresses casual engagement.
- Badges/contributor mechanics ("Proverb Keeper", recording tasks, translation votes) are a
  **later phase**, but the XP-rewarded correction is the seed planted now.

---

## 9. Scope

**In the pilot:** 2 characters (9 PNGs), `mascot.js` + slots, wiring into Home/Translate/Teach/
Grammar/Proverbs/Search, rewarded corrections, reuse of existing streak/XP, hiding developer
metadata from users on Translate.

**Explicitly OUT (later phases):** hearts/energy system, mini-games beyond existing Teach, leagues,
mobile-money bundles, contributor badges/leaderboards, a 3rd/4th character, an elder Jajja, and the
Style-B 3D rebuild.

---

## 10. Success criteria ("see how it works out")

The pilot succeeds if, after shipping:
1. The app demonstrably feels more alive (subjective, Patrick's call + any user reaction).
2. The Translate correction flow is visibly simpler and the mascot reacts correctly at each step
   (verified live, console-clean, on mobile width).
3. We have a working `mascot.js` pattern that a 3rd/4th character — or a Style-B 3D swap — can plug
   into without touching app logic.
4. We learn enough to answer: how many more characters, and which content needs its own persona
   (e.g., does Proverbs deserve a dedicated elder)?

---

## Appendix A — Draft image-to-image prompts (to refine on plan approval)

Shared preamble for every prompt: *"Use the attached image as the exact character — keep the same
face, skin tone, hair, shirt, and loose black-ink pen-sketch line style on cream paper. Waist-up,
centered, transparent background, same line weight. Only change the pose and expression to:"*

**Kintu (from grinning ROAARR boy):**
- `cheering` — big grin, one thumb up, looking at viewer
- `happy` — gentle smile, small approving nod
- `celebrate` — both arms raised, mouth open in cheer, eyes bright
- `oops` — sheepish half-smile, one hand scratching head, eyes glancing away
- `thinking` — looking up, one finger to chin, curious

**Nambi (from sassy girl with twists):**
- `neutral` — relaxed friendly expression, open hands, sass softened
- `explaining` — one hand pointing/presenting, mouth mid-speech
- `challenging` — hands on hips, raised eyebrow, confident smirk
- `impressed` — approving nod, slight smile, one eyebrow up

(Final prompts tuned during implementation once Patrick test-generates the first 1–2 and we confirm
the tool holds character identity.)
