# Creatorly-Inspired Redesign — Design Spec
**Date:** 2026-05-10  
**Status:** Approved for implementation  
**Priority order:** translate → teach → search → index → admin

---

## 1. Goal

Transform Luganda AI Studio from a dark green sidebar app into a mobile-first, dual-mode (light + dark) product inspired by Creatorly's visual language — while keeping all existing functionality intact.

---

## 2. Design Decisions (locked)

| Decision | Choice | Rationale |
|---|---|---|
| Mobile nav | Hybrid: 4-tab bottom bar (mobile) + sidebar (desktop) | Best mobile UX without breaking desktop |
| Light mode | Cream `#E8E6DE` bg, `#1C2B1A` text, lime `#CADF3E` accent | Exact Creatorly palette |
| Dark mode | `#0D1117` bg, `#E6EDF3` text, lime `#CADF3E` accent | Consistent accent across modes |
| Theme toggle | Pill toggle on home page (mobile) + sidebar bottom (desktop) | Visible design feature, not buried utility |
| Display font | Figtree 800 | Distinctive, clean, closest to Creatorly's energy |
| Body font | DM Sans 400–600 | Keep — already loaded, no change needed |
| Buttons | Lime pill (`border-radius: 50px`), dark label | Direct match to Creatorly CTA style |

---

## 3. Token System

All per-page inline CSS token blocks are removed. A single `frontend/styles.css` owns the full token set.

### 3.1 Light mode (default)

```css
:root {
  --bg:             #E8E6DE;
  --bg-card:        #F5F4F0;
  --bg-card-hover:  #EDEAE2;
  --bg-input:       #FFFFFF;
  --border:         #D4D0C8;
  --border-focus:   #CADF3E;

  --lime:           #CADF3E;
  --lime-dim:       #B8CC2A;
  --lime-dark:      #8FA800;
  --lime-glow:      rgba(202, 223, 62, 0.25);
  --lime-bg:        rgba(202, 223, 62, 0.12);

  --text-primary:   #1C2B1A;
  --text-secondary: #5A6B5A;
  --text-muted:     #8A9A8A;
  --text-on-lime:   #1C2B1A;

  --green:          #2E7D32;
  --red:            #C62828;
  --red-bg:         #FFEBEE;
  --red-border:     #EF9A9A;
  --success:        #2E7D32;
  --success-bg:     #E8F5E9;
  --success-border: #A5D6A7;
  --amber:          #F57F17;
  --amber-bg:       #FFF8E1;
  --amber-border:   #FFE082;

  --font-display:   'Figtree', sans-serif;
  --font-body:      'DM Sans', sans-serif;

  --radius-pill:    50px;
  --radius-lg:      16px;
  --radius:         12px;
  --radius-sm:      8px;
  --radius-xs:      4px;

  --shadow-card:    0 1px 4px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.06);
  --shadow-modal:   0 8px 40px rgba(0,0,0,0.16);
  --transition:     0.18s ease;
  --transition-slow:0.32s ease;
}
```

### 3.2 Dark mode

```css
[data-theme="dark"] {
  --bg:             #0D1117;
  --bg-card:        #161B22;
  --bg-card-hover:  #1C2330;
  --bg-input:       #0D1117;
  --border:         #30363D;
  --border-focus:   #CADF3E;

  --text-primary:   #E6EDF3;
  --text-secondary: #8B949E;
  --text-muted:     #484F58;
  --text-on-lime:   #0D1117;

  --green:          #3FB950;
  --red:            #F85149;
  --red-bg:         #1E0A0A;
  --red-border:     #5C1A1A;
  --success:        #3FB950;
  --success-bg:     #091A0F;
  --success-border: #1A4A28;
  --amber:          #F0A500;
  --amber-bg:       #1C1205;
  --amber-border:   #7A5212;

  --shadow-card:    0 1px 4px rgba(0,0,0,0.4), 0 4px 16px rgba(0,0,0,0.3);
  --shadow-modal:   0 8px 40px rgba(0,0,0,0.6);
  /* --lime, --font-*, --radius-* unchanged */
}
```

### 3.3 Theme persistence

```js
// In <head>, before any render — prevents flash
(function() {
  const t = localStorage.getItem('theme');
  if (t === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
})();
```

Toggle function (shared across all pages):
```js
function toggleTheme() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  document.documentElement.setAttribute('data-theme', isDark ? 'light' : 'dark');
  localStorage.setItem('theme', isDark ? 'light' : 'dark');
  updateToggleUI();
}
```

---

## 4. Navigation Architecture

### 4.1 Desktop (≥769px) — Sidebar unchanged in structure

The sidebar keeps its current layout. Changes:
- Background uses `--bg-card` (adapts per mode)
- Active link gets a `border-left: 3px solid var(--lime)` accent instead of green
- Brand icon becomes a Figtree bold wordmark
- **New:** Lime pill theme toggle added above the version tag at the bottom

Pill toggle (sidebar):
```html
<div class="theme-pill">
  <button class="theme-pill-btn" id="btnLight" onclick="setTheme('light')">☀ Light</button>
  <button class="theme-pill-btn" id="btnDark"  onclick="setTheme('dark')">🌙 Dark</button>
</div>
```

### 4.2 Mobile (≤768px) — Bottom tab bar replaces hamburger drawer

The sidebar is hidden entirely on mobile. A fixed bottom nav bar replaces it.

**4 primary tabs:**
| Tab | Label | Page |
|---|---|---|
| ⌂ | Home | `index.html` |
| ⇄ | Translate | `translate.html` |
| ◎ | Search | `search.html` |
| 📖 | Teach | `teach.html` |

**Secondary links** (Reviews, Admin, API Docs): Accessible from the Home page via a "More" section — a list of secondary link cards below the feature grid. No overflow tab needed.

**Bottom nav HTML** (included in every page):
```html
<nav class="bottom-nav">
  <a href="index.html"     class="bnav-item" data-page="index">
    <span class="bnav-icon">⌂</span>
    <span class="bnav-label">Home</span>
  </a>
  <a href="translate.html" class="bnav-item" data-page="translate">
    <span class="bnav-icon">⇄</span>
    <span class="bnav-label">Translate</span>
  </a>
  <a href="search.html"    class="bnav-item" data-page="search">
    <span class="bnav-icon">◎</span>
    <span class="bnav-label">Search</span>
  </a>
  <a href="teach.html"     class="bnav-item" data-page="teach">
    <span class="bnav-icon">📖</span>
    <span class="bnav-label">Teach</span>
  </a>
</nav>
```

Active tab is set via `data-page` matching the current filename.

**Page body** gets `padding-bottom: 80px` on mobile to clear the bottom nav.

### 4.3 Mobile topbar (simplified)

No hamburger. Just:
```
[Page title]              [☀/🌙 icon toggle]
```
The theme icon toggle is the only item in the top-right on mobile pages (not the home page, which has the full pill).

---

## 5. Component Specifications

### 5.1 Primary button (lime pill)

```css
.btn-primary {
  background: var(--lime);
  color: var(--text-on-lime);
  border: none;
  border-radius: var(--radius-pill);
  padding: 14px 28px;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 15px;
  cursor: pointer;
  transition: background var(--transition), transform var(--transition), box-shadow var(--transition);
  min-height: 48px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.btn-primary:hover  { background: var(--lime-dim); transform: translateY(-1px); box-shadow: 0 4px 16px var(--lime-glow); }
.btn-primary:active { transform: translateY(0); box-shadow: none; }
```

### 5.2 Secondary button (pill outline)

```css
.btn-secondary {
  background: var(--bg-card);
  color: var(--text-secondary);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-pill);
  padding: 13px 24px;
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: border-color var(--transition), color var(--transition);
  min-height: 48px;
}
.btn-secondary:hover { border-color: var(--lime); color: var(--text-primary); }
```

### 5.3 Cards

```css
.card {
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  box-shadow: var(--shadow-card);
  transition: border-color var(--transition), box-shadow var(--transition);
}
.card:hover { border-color: var(--lime); }
```

Feature cards on index get a lime left-accent border on hover:
```css
.feature-card:hover { border-left: 3px solid var(--lime); }
```

### 5.4 Inputs

```css
.input-field {
  background: var(--bg-input);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 16px;
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: 16px; /* 16px prevents iOS zoom */
  outline: none;
  transition: border-color var(--transition), box-shadow var(--transition);
  width: 100%;
}
.input-field:focus {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px var(--lime-glow);
}
```

### 5.5 Chips / badges

Confidence and match-type chips keep their semantic colours (green/amber/red) but use the new bg variables so they work in both modes.

### 5.6 Hero (index.html)

```html
<div class="hero">
  <div class="hero-kicker">Luganda AI Studio</div>
  <h1 class="hero-title">
    Translate.<br>
    Learn.<br>
    <span class="hero-underline">Communicate.</span>
  </h1>
  <p class="hero-desc">AI-powered tools for the Luganda language — built to run on your machine.</p>
  <a href="translate.html" class="btn-primary hero-cta">Start Translating →</a>
</div>
```

```css
.hero-title {
  font-family: var(--font-display);
  font-size: clamp(2.4rem, 8vw, 4rem);
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.1;
  letter-spacing: -0.02em;
}
.hero-underline {
  text-decoration: underline;
  text-decoration-color: var(--lime);
  text-decoration-thickness: 4px;
  text-underline-offset: 4px;
}
```

### 5.7 Theme pill toggle (home + sidebar)

```css
.theme-pill {
  display: flex;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-pill);
  padding: 4px;
  gap: 2px;
}
.theme-pill-btn {
  flex: 1;
  padding: 8px 16px;
  border-radius: var(--radius-pill);
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background var(--transition), color var(--transition);
}
.theme-pill-btn.active {
  background: var(--lime);
  color: var(--text-on-lime);
}
```

---

## 6. Responsive Breakpoints

| Breakpoint | Layout |
|---|---|
| ≥769px | Sidebar (220px) + main content. No bottom nav. |
| 375–768px | No sidebar. Bottom tab bar (64px). Top bar: title + theme icon. |
| <375px | Same as above. Single-column, larger touch targets (52px min). |

iOS safe area: `padding-bottom: calc(64px + env(safe-area-inset-bottom))` on bottom nav.

Touch target minimum: 48px height on all interactive elements.

---

## 7. Font Loading

Replace current Google Fonts import with:
```html
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;600;700;800&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&display=swap" rel="stylesheet" />
```

Figtree replaces Fraunces on all pages. DM Sans keeps its current weights.

---

## 8. Files Changed

| File | Change type | Notes |
|---|---|---|
| `frontend/styles.css` | Full rewrite | New token system, bottom nav, buttons, cards |
| `frontend/translate.html` | Inline styles → shared classes | Direction toggle, translate button, output card |
| `frontend/teach.html` | Inline styles → shared classes | Flash cards, quiz buttons |
| `frontend/search.html` | Inline styles → shared classes | Search bar, result cards |
| `frontend/index.html` | Full restructure | Hero, feature cards, theme pill, secondary links |
| `frontend/admin.html` | Token update only | Minimal structural change |
| `frontend/reviews.html` | Token update only | Minimal structural change |

---

## 9. Implementation Order

1. `styles.css` — tokens + bottom nav + shared components (unblocks everything)
2. `translate.html` — highest-priority page, inline styles replaced
3. `teach.html`
4. `search.html`
5. `index.html` — hero + theme pill + feature cards
6. `admin.html` + `reviews.html` — token sweep only

---

## 10. What Is NOT Changing

- All API endpoints and backend logic — untouched
- JavaScript functionality (translation, feedback, session history, TTS, search) — untouched  
- PWA manifest and service worker — untouched
- ChromaDB collections and data — untouched
- `chat.html` — not in scope for this redesign
