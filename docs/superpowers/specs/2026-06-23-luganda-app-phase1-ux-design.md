# Luganda App — Phase 1 UI/UX Redesign Spec

**Scope:** Per the approved 5-phase roadmap (`C:\Users\patri\.claude\plans\luganda-ai-studio-should-reflective-candy.md`),
this covers **UI/UX only** — Home onboarding, Translate, Search, Teach. Pricing/monetisation
is Phase 3 and explicitly out of scope here.

**Competitors benchmarked:** Duolingo (onboarding, gamified streaks, no hearts paywall),
Merriam-Webster (dictionary word-pages), NKENNE (African-language, culture-first, offline-first).
No screenshots were available this session — analysis is from general knowledge of each app,
checked against the actual current code (`frontend/index.html`, `translate.html`, `search.html`,
`teach.html`).

---

## Current state (grounded in code, read 2026-06-23)

- **Nav:** desktop sidebar + mobile bottom-nav already correctly scoped to 4 user-facing
  tabs (Home/Translate/Search/Teach) — Reviews/Admin are sidebar-only, not in the mobile
  bottom-nav. No change needed here.
- **Home (`index.html`):** static marketing hero ("Translate. Learn. Communicate."), a raw
  stats row (`statVocab`, `statSentences`, etc. — exposes internal record counts to end users),
  a 4-card feature grid. No personalization, no streak, no "what do I do next."
- **Translate (`translate.html`):** already has direction toggle, input/output cards, a
  feedback row (✓/✗/🔁), and an "Expected Output" correction field — solid mechanics from
  Phase 0. Copy is technical: empty state says "No translation found in the current dataset,"
  output panel is labelled "Output."
- **Search (`search.html`):** keyword search + filter chips (All/Vocabulary/Sentences/
  Grammar/Proverbs/Documents) + 6 suggestion chips. Results area not yet inspected in detail,
  but the page is a flat results list, not a Merriam-Webster-style word-page.
- **Teach (`teach.html`):** already has Flash Cards / Quiz mode toggle, a progress bar, and
  got-it/try-again counters. **No streak, no XP, no levelled paths exist anywhere in the
  codebase** (confirmed via grep across `frontend/*.html` and `app.js`) — this is the single
  biggest gap vs Duolingo.

## 8-angle gap table

| # | Angle | Competitor pattern | Luganda app now | Gap | Fix (this phase) |
|---|-------|--------------------|--------------------|-----|-------------------|
| 1 | Header/identity | Duolingo: streak flame + gem count always visible | Mobile topbar = page title + theme toggle only | No progress/identity signal | Add a streak pill to the mobile topbar (becomes meaningful once Teach has a streak) |
| 2 | Bottom nav | Duolingo: 4-5 tabs, filled active icon | Already 4 tabs, scoped correctly | None | No change |
| 3 | Home/dashboard | Duolingo: greeting + streak hero + single "Continue" CTA. Merriam-Webster: search-first. NKENNE: culture/offline framing | Static tagline hero + raw internal stat counts + 4-card grid | Raw counts mean nothing to a new user; no personalized CTA; no culture/offline trust signal | Replace stat row with a friendlier framing (e.g. "622 words and phrases verified by native speakers" instead of bare numbers split by collection type); add first-time vs returning-user hero state (see Task 2 below) |
| 4 | Translate | Merriam-Webster: warm, dictionary-style copy | Mechanically solid, copy is technical/clinical | "No translation found in the current dataset" reads like a database error | Reword empty/error-state copy to be encouraging and explain the correction loop in plain language |
| 5 | Search/dictionary | Merriam-Webster: word-page with POS, both-direction gloss, examples, audio, related words | Flat filtered search list | Not yet a true "word page" experience | Out of scope for this pass — flagged as a Phase 2 (translation accuracy/data depth) follow-on once search ranking is fixed, since a word-page is only as good as the ranking underneath it |
| 6 | Teach/Quiz | Duolingo: streaks + XP + NO hearts paywall, short levelled paths | Flash/Quiz toggle + got-it/try-again counts, no streak/XP at all | Biggest gap — zero gamification despite UI structure already supporting progress display | Add a simple daily streak counter (localStorage-based, no backend dependency) and a session XP tally; explicitly do not add hearts/lives |
| 7 | About/trust | NKENNE: offline-first + culture-first copy | `sidebar-version` just shows "v1.0 · Luganda AI Studio," no trust signal anywhere | Missing entirely | Add one short trust line to the home hero area: native-speaker-verified data note |
| 8 | Monetisation | Duolingo: gem shop, no aggressive paywall | None yet | n/a — correctly deferred | Out of scope (Phase 3) |

## What this phase builds (concrete tasks)

1. **Home hero rework** (`frontend/index.html`): replace raw stat row framing with
   user-friendly copy; add a one-line native-speaker-verified trust note; keep the existing
   feature grid (it already matches the competitor pattern reasonably well).
2. **Streak + XP system for Teach** (`frontend/teach.html` + new small JS module): client-side
   only, `localStorage`-backed daily streak (increments once per calendar day a quiz/flashcard
   session completes) and a simple session XP counter. No backend table needed yet — matches
   the "don't bolt on payment/backend work prematurely" principle from `polish-and-price`.
   Surface the streak in the mobile topbar via a small pill component reused across pages.
3. **Translate empty/error copy rewrite** (`frontend/translate.html`): replace the two
   technical-sounding strings (`stateNotFound`, error text) with warmer, plain-language copy
   that explains the correction-save loop already built in Phase 0.
4. **Explicitly NOT building this phase:** word-page redesign for Search (depends on Phase 2
   search-ranking fix), any payment/tier UI (Phase 3), onboarding account flow changes (no
   auth system exists yet in this app — confirm before assuming one needs building).

## Verification

- Manual click-through on a phone-sized viewport: Home shows friendly copy, not raw counts.
- Complete one Teach session → streak counter increments, persists across a page reload
  (`localStorage`), resets correctly on a new calendar day (manually fake the stored date to
  confirm reset logic, since waiting a real day isn't practical to test).
- Translate "Wrong" → correction flow still works end-to-end after copy changes (regression
  check against the Phase 0 feedback fix).
- No layout shift introduced — check trimmed-down `nextjs-dashboard-cls-fix` principles even
  though this isn't Next.js (same idea: don't let async-loaded streak data cause a jump).
