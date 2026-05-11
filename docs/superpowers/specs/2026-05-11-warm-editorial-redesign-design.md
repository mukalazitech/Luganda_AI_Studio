# Warm Editorial Redesign — Design Spec
**Date:** 2026-05-11  
**Status:** Approved  
**Scope:** `frontend/styles.css` (full token replacement) + `frontend/index.html` (hero layout fix)  
**All other pages** inherit new tokens automatically — no HTML changes needed outside index.html.

---

## 1. Problem

The current design system (warm beige + lime green) looks flat and generic on mobile:
- Visual hierarchy is broken — title, CTA, cards, and stats all feel the same weight
- `#CADF3E` lime reads as a productivity app accent, not a language/cultural tool
- Hero CTA sits awkwardly beside a theme toggle pill at the same visual height
- Feature cards have no dominant accent — borders and shadows are too subtle
- Stats row wraps unpredictably on mobile

## 2. Solution: Warm Editorial Design System

Replace the current tokens with a **terracotta + warm cream** palette. Fix hierarchy through size and accent weight, not decoration.

---

## 3. Color Tokens

### Light Mode

| CSS Variable | Old Value | New Value | Notes |
|---|---|---|---|
| `--bg` | `#E8E6DE` | `#F7F0E6` | Warmer, creamier base |
| `--bg-card` | `#F5F4F0` | `#FFF8EF` | Soft warm white for cards |
| `--bg-card-hover` | `#EDEAE2` | `#F5EAD8` | Hover state, slightly darker cream |
| `--bg-input` | `#FFFFFF` | `#FFFFFF` | Unchanged |
| `--border` | `#D4D0C8` | `#E2D5C3` | Warmer border tone |
| `--border-focus` | `#CADF3E` | `#C1440E` | Terracotta focus ring |
| `--lime` | `#CADF3E` | `#C1440E` | **Renamed intent: --primary** (terracotta) |
| `--lime-dim` | `#B8CC2A` | `#A83A0C` | Hover on primary |
| `--lime-dark` | `#8FA800` | `#8C2E08` | Dark variant for text/links |
| `--lime-glow` | `rgba(202,223,62,0.25)` | `rgba(193,68,14,0.20)` | Focus glow |
| `--lime-bg` | `rgba(202,223,62,0.12)` | `rgba(193,68,14,0.08)` | Active bg tint |
| `--text-primary` | `#1C2B1A` | `#2C1810` | Deep warm brown |
| `--text-secondary` | `#5A6B5A` | `#7A5A48` | Mid warm brown |
| `--text-muted` | `#8A9A8A` | `#B09070` | Light warm tan |
| `--text-on-lime` | `#1C2B1A` | `#F7F0E6` | Text on terracotta buttons |
| `--amber` | `#F57F17` | `#E8A87C` | Softer amber for warnings |
| `--amber-bg` | `#FFF8E1` | `#FDF3E8` | Warmer amber bg |
| `--amber-border` | `#FFE082` | `#DEBA96` | Warmer amber border |

### Dark Mode

| CSS Variable | New Value | Notes |
|---|---|---|
| `--bg` | `#1C1208` | Very dark warm brown (not cold black) |
| `--bg-card` | `#261A0E` | Slightly lighter, same warmth |
| `--bg-card-hover` | `#301F10` | Hover state |
| `--bg-input` | `#1C1208` | Same as bg |
| `--border` | `#3A2818` | Dark warm border |
| `--text-primary` | `#F5EDD8` | Aged cream — warmer than pure white |
| `--text-secondary` | `#A08060` | Mid warm |
| `--text-muted` | `#6A5040` | Dark tan |
| `--text-on-lime` | `#1C1208` | Text on terracotta (dark mode terracotta is lighter) |
| `--lime` (primary) | `#E8824A` | Lighter terracotta readable on dark bg |
| `--lime-dim` | `#D06A38` | Hover |
| `--lime-dark` | `#C05830` | Links/accents |

All other dark mode tokens (success, red, shadows) remain unchanged.

---

## 4. Typography Scale

Fonts unchanged: **Figtree** (display) + **DM Sans** (body).

| Element | Old Mobile Size | New Mobile Size | Rationale |
|---|---|---|---|
| `.hero-title` | `clamp(1.75rem, 7vw, 2.5rem)` | `clamp(2.4rem, 9vw, 3.2rem)` | Must dominate — hierarchy anchor |
| `.hero-desc` | `0.95rem` | `0.88rem` | Subordinate to title, not competing |
| `.page-title` | `clamp(1.35rem, 5vw, 1.8rem)` | unchanged | Already correct |
| `.feature-card-title` | `0.95rem` | `1rem, 600wt` | Slightly more weight |
| `.stat-value` | `1.4rem` | `1.5rem` | More visual presence |
| `.btn-primary` font | `14px` | `15px` | Match desktop |

---

## 5. Component Changes

### Hero section (`index.html`)
- Title size increased (see typography table)
- CTA button: full-width on mobile (`width: 100%`), `border-radius: 8px` (not pill), standalone row
- Theme pill: stays in hero but on its own row below the CTA, `width: fit-content`
- Remove the awkward side-by-side CTA + pill layout

### Feature cards
- Left accent stripe: `border-left: 3px solid var(--lime)` (was transparent)
- Remove box shadow — the stripe carries the visual weight
- Padding: `18px 16px 18px 20px` to account for stripe
- Hover: `border-left-color` brightens + `translateY(-2px)` + terracotta glow

### Stats row (mobile)
- Becomes a 4-column inset box: `background: var(--bg-card); border-radius: 10px`
- Each stat cell has a right border divider
- Stat numbers: `1.5rem, 800wt` in `--text-primary`
- Stat labels: `0.6rem, uppercase, --text-muted`

### Bottom nav
- Background: `var(--bg-card)` (FFF8EF cream)
- Active item: small filled pill `background: var(--lime-bg)` behind icon + label
- Height stays `64px`

### Buttons
- `--btn-radius`: `8px` for `.btn-primary` on mobile (was pill `50px`) — more editorial, less app-like
- Desktop keeps pill shape — change only applies via mobile media query
- `min-height` stays `44px` everywhere

---

## 6. Files Changed

| File | Change type | What changes |
|---|---|---|
| `frontend/styles.css` | Replace | All `:root` tokens + dark mode tokens + hero/card/button mobile rules |
| `frontend/index.html` | Minor edit | Hero flex layout: CTA full-width, theme pill below on its own row |

No other HTML files change. All pages (translate, search, teach, reviews, admin) inherit new tokens automatically.

---

## 7. What Does NOT Change

- All JavaScript logic and API calls
- Page structure and navigation
- Responsive breakpoints (768px / 480px / 374px)
- Font families
- Component class names (no HTML refactor beyond index.html hero)
- Dark mode toggle mechanism
- All functional features

---

## 8. Success Criteria

- On a 360px phone: hero title is visually dominant, CTA is full-width and tappable, stats fit in one row without wrapping
- Feature cards have clear accent stripe and readable text at all sizes
- Terracotta accent is consistent across all pages (focus rings, active states, chips)
- Dark mode reads as warm dark brown, not cold tech-grey
- No horizontal scroll at any width
