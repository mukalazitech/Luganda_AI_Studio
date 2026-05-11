# Creatorly-Inspired Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform Luganda AI Studio from a dark-only amber/green sidebar app into a dual-mode (light + dark), mobile-first product using the Creatorly visual language — lime accent, Figtree display font, bottom tab nav on mobile — without touching any backend logic.

**Architecture:** A single shared `frontend/styles.css` owns the entire design token system, layout, and component library. Each HTML page strips its inline `<style>` block and references only shared classes. Theme switching is driven by a `data-theme` attribute on `<html>`, persisted to `localStorage` with a flash-prevention script in `<head>`.

**Tech Stack:** Static HTML/CSS/JS served by FastAPI StaticFiles. Google Fonts (Figtree + DM Sans). No build step. No new dependencies.

---

## File Map

| File | Action | What changes |
|---|---|---|
| `frontend/styles.css` | Full rewrite | New token system, dual-mode, bottom nav, all shared components |
| `frontend/index.html` | Restructure | Strip inline styles, add hero, feature cards, theme pill, secondary links, bottom nav |
| `frontend/translate.html` | Refactor | Strip inline styles, use shared classes, add bottom nav + topbar theme toggle |
| `frontend/teach.html` | Refactor | Strip inline styles, use shared classes, add bottom nav + topbar theme toggle |
| `frontend/search.html` | Refactor | Strip inline styles, use shared classes, add bottom nav + topbar theme toggle |
| `frontend/admin.html` | Token sweep | Replace hardcoded colours with CSS vars, add bottom nav |
| `frontend/reviews.html` | Token sweep | Replace hardcoded colours with CSS vars, add bottom nav |

---

## Task 1: Rewrite `frontend/styles.css`

**Files:**
- Modify: `frontend/styles.css` (full rewrite)

This task unblocks everything else. All shared tokens, layout, nav, and components live here.

- [ ] **Step 1: Read the current file**

```bash
cat -n frontend/styles.css
```

Note the current structure so nothing critical is accidentally dropped.

- [ ] **Step 2: Replace the entire file with the new design system**

Replace the full content of `frontend/styles.css` with:

```css
/* frontend/styles.css — Luganda AI Studio — Creatorly Design System */

/* ── Reset ──────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 16px; scroll-behavior: smooth; }
.hidden { display: none !important; }

/* ── Tokens: Light mode (default) ───────────────────────────────────── */
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

/* ── Tokens: Dark mode ───────────────────────────────────────────────── */
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
}

/* ── Base ────────────────────────────────────────────────────────────── */
body {
  background: var(--bg);
  color: var(--text-primary);
  font-family: var(--font-body);
  font-weight: 400;
  line-height: 1.6;
  min-height: 100vh;
}

a { color: var(--lime-dark); text-decoration: none; }
a:hover { text-decoration: underline; }

/* ── Sidebar (desktop ≥769px) ────────────────────────────────────────── */
.app-shell {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: var(--bg-card);
  border-right: 1.5px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 24px 0;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

.sidebar-brand {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 1.1rem;
  color: var(--text-primary);
  padding: 0 20px 24px;
  border-bottom: 1.5px solid var(--border);
  margin-bottom: 12px;
  letter-spacing: -0.01em;
}

.sidebar-brand span { color: var(--lime-dark); }

.sidebar-nav { flex: 1; padding: 0 10px; }

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
  transition: color var(--transition), background var(--transition), border-color var(--transition);
  border-left: 3px solid transparent;
  margin-bottom: 2px;
}

.sidebar-link:hover {
  color: var(--text-primary);
  background: var(--bg-card-hover);
  text-decoration: none;
}

.sidebar-link.active {
  color: var(--text-primary);
  background: var(--lime-bg);
  border-left-color: var(--lime);
  font-weight: 600;
}

.sidebar-footer {
  padding: 16px 16px 0;
  border-top: 1.5px solid var(--border);
}

.sidebar-version {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-align: center;
  margin-top: 8px;
}

/* ── Theme pill toggle ───────────────────────────────────────────────── */
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
  padding: 7px 12px;
  border-radius: var(--radius-pill);
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background var(--transition), color var(--transition);
  white-space: nowrap;
}

.theme-pill-btn.active {
  background: var(--lime);
  color: var(--text-on-lime);
}

/* ── Mobile topbar ───────────────────────────────────────────────────── */
.mobile-topbar {
  display: none;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  height: 56px;
  background: var(--bg-card);
  border-bottom: 1.5px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.mobile-topbar-title {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1rem;
  color: var(--text-primary);
}

.theme-icon-btn {
  background: none;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1rem;
  color: var(--text-secondary);
  transition: border-color var(--transition), color var(--transition);
}

.theme-icon-btn:hover { border-color: var(--lime); color: var(--text-primary); }

/* ── Bottom tab nav (mobile ≤768px) ──────────────────────────────────── */
.bottom-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--bg-card);
  border-top: 1.5px solid var(--border);
  z-index: 200;
  padding-bottom: env(safe-area-inset-bottom);
}

.bottom-nav-inner {
  display: flex;
  height: 64px;
}

.bnav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 600;
  text-decoration: none;
  transition: color var(--transition);
  min-height: 48px;
}

.bnav-item:hover { text-decoration: none; }

.bnav-item.active { color: var(--lime-dark); }

.bnav-icon { font-size: 1.2rem; line-height: 1; }

.bnav-label { font-family: var(--font-body); }

/* ── Main content area ───────────────────────────────────────────────── */
.main-content {
  flex: 1;
  min-width: 0;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 24px;
}

/* ── Buttons ─────────────────────────────────────────────────────────── */
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
  text-decoration: none;
}

.btn-primary:hover {
  background: var(--lime-dim);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px var(--lime-glow);
  text-decoration: none;
  color: var(--text-on-lime);
}

.btn-primary:active { transform: translateY(0); box-shadow: none; }

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
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-secondary:hover { border-color: var(--lime); color: var(--text-primary); }

.btn-ghost {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-family: var(--font-body);
  font-size: 14px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  transition: color var(--transition), background var(--transition);
}

.btn-ghost:hover { color: var(--text-primary); background: var(--bg-card-hover); }

/* ── Cards ───────────────────────────────────────────────────────────── */
.card {
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  box-shadow: var(--shadow-card);
  transition: border-color var(--transition);
}

.card:hover { border-color: var(--lime); }

/* ── Inputs ──────────────────────────────────────────────────────────── */
.input-field {
  background: var(--bg-input);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 16px;
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: 16px;
  outline: none;
  width: 100%;
  transition: border-color var(--transition), box-shadow var(--transition);
}

.input-field:focus {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px var(--lime-glow);
}

textarea.input-field { resize: vertical; min-height: 100px; }

/* ── Chips / Badges ──────────────────────────────────────────────────── */
.chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  font-size: 0.75rem;
  font-weight: 600;
  font-family: var(--font-body);
}

.chip-success { background: var(--success-bg); color: var(--success); border: 1px solid var(--success-border); }
.chip-amber   { background: var(--amber-bg);   color: var(--amber);   border: 1px solid var(--amber-border); }
.chip-red     { background: var(--red-bg);     color: var(--red);     border: 1px solid var(--red-border); }
.chip-neutral { background: var(--bg-card);    color: var(--text-secondary); border: 1px solid var(--border); }
.chip-lime    { background: var(--lime-bg);    color: var(--lime-dark); border: 1px solid var(--lime); }

/* ── Section / Page header ───────────────────────────────────────────── */
.page-header {
  padding: 32px 0 24px;
  border-bottom: 1.5px solid var(--border);
  margin-bottom: 32px;
}

.page-title {
  font-family: var(--font-display);
  font-size: clamp(1.6rem, 4vw, 2.2rem);
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  line-height: 1.15;
}

.page-sub {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-top: 6px;
}

/* ── Hero (index.html) ───────────────────────────────────────────────── */
.hero {
  padding: 48px 0 40px;
}

.hero-kicker {
  font-family: var(--font-body);
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--lime-dark);
  margin-bottom: 16px;
}

.hero-title {
  font-family: var(--font-display);
  font-size: clamp(2.4rem, 8vw, 4rem);
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.1;
  letter-spacing: -0.02em;
  margin-bottom: 20px;
}

.hero-underline {
  text-decoration: underline;
  text-decoration-color: var(--lime);
  text-decoration-thickness: 4px;
  text-underline-offset: 4px;
}

.hero-desc {
  font-size: 1.05rem;
  color: var(--text-secondary);
  max-width: 500px;
  line-height: 1.7;
  margin-bottom: 28px;
}

/* ── Feature grid (index.html) ───────────────────────────────────────── */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  margin: 32px 0;
}

.feature-card {
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-card);
  transition: border-color var(--transition), border-left-color var(--transition), transform var(--transition);
  border-left: 3px solid transparent;
  text-decoration: none;
  display: block;
  color: var(--text-primary);
}

.feature-card:hover {
  border-left-color: var(--lime);
  border-color: var(--lime);
  transform: translateY(-2px);
  text-decoration: none;
  color: var(--text-primary);
}

.feature-card-icon { font-size: 1.6rem; margin-bottom: 10px; }
.feature-card-title { font-family: var(--font-display); font-weight: 700; font-size: 1rem; margin-bottom: 4px; }
.feature-card-desc  { font-size: 0.85rem; color: var(--text-secondary); }

/* ── Secondary links (index.html More section) ───────────────────────── */
.more-section { margin-top: 40px; padding-top: 32px; border-top: 1.5px solid var(--border); }
.more-title { font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 12px; }
.more-links { display: flex; flex-wrap: wrap; gap: 8px; }
.more-link {
  padding: 8px 16px;
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-pill);
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
  transition: border-color var(--transition), color var(--transition);
  text-decoration: none;
}
.more-link:hover { border-color: var(--lime); color: var(--text-primary); text-decoration: none; }

/* ── Stats row ───────────────────────────────────────────────────────── */
.stats-row { display: flex; gap: 24px; flex-wrap: wrap; margin: 24px 0; }
.stat-item { display: flex; flex-direction: column; }
.stat-value { font-family: var(--font-display); font-weight: 800; font-size: 1.6rem; color: var(--text-primary); }
.stat-label { font-size: 0.8rem; color: var(--text-muted); }

/* ── Direction toggle (translate.html) ───────────────────────────────── */
.direction-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-pill);
  padding: 6px;
  width: fit-content;
}

.dir-btn {
  padding: 8px 20px;
  border-radius: var(--radius-pill);
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: background var(--transition), color var(--transition);
}

.dir-btn.active { background: var(--lime); color: var(--text-on-lime); }

/* ── TTS button ──────────────────────────────────────────────────────── */
.tts-btn {
  background: none;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 6px 10px;
  cursor: pointer;
  font-size: 1rem;
  color: var(--text-secondary);
  transition: border-color var(--transition), color var(--transition);
}
.tts-btn:hover { border-color: var(--lime); color: var(--text-primary); }
.tts-btn.loading { animation: pulse 1s infinite; }

@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.4; } }

/* ── Feedback buttons ────────────────────────────────────────────────── */
.feedback-row { display: flex; gap: 8px; flex-wrap: wrap; }

.feedback-btn {
  padding: 8px 16px;
  border-radius: var(--radius-pill);
  border: 1.5px solid var(--border);
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
  min-height: 36px;
}

.feedback-btn:hover { border-color: var(--lime); color: var(--text-primary); }
.feedback-btn.selected-correct { background: var(--success-bg); border-color: var(--success); color: var(--success); }
.feedback-btn.selected-wrong   { background: var(--red-bg);     border-color: var(--red);     color: var(--red); }
.feedback-btn.selected-review  { background: var(--amber-bg);   border-color: var(--amber);   color: var(--amber); }

/* ── Search result cards ─────────────────────────────────────────────── */
.result-card {
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  transition: border-color var(--transition);
  margin-bottom: 10px;
}
.result-card:hover { border-color: var(--lime); }

/* ── Toast notification ──────────────────────────────────────────────── */
.toast {
  position: fixed;
  bottom: 80px;
  right: 20px;
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 18px;
  font-size: 0.875rem;
  color: var(--text-primary);
  box-shadow: var(--shadow-modal);
  z-index: 300;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity var(--transition), transform var(--transition);
  pointer-events: none;
}

.toast.show { opacity: 1; transform: translateY(0); }

/* ── Utility ─────────────────────────────────────────────────────────── */
.text-muted    { color: var(--text-muted); }
.text-secondary{ color: var(--text-secondary); }
.text-lime     { color: var(--lime-dark); }
.text-success  { color: var(--success); }
.text-red      { color: var(--red); }
.text-amber    { color: var(--amber); }

.mt-4  { margin-top: 4px; }
.mt-8  { margin-top: 8px; }
.mt-12 { margin-top: 12px; }
.mt-16 { margin-top: 16px; }
.mt-24 { margin-top: 24px; }
.mt-32 { margin-top: 32px; }

.mb-8  { margin-bottom: 8px; }
.mb-16 { margin-bottom: 16px; }
.mb-24 { margin-bottom: 24px; }

.gap-8  { gap: 8px; }
.gap-12 { gap: 12px; }
.gap-16 { gap: 16px; }

.flex   { display: flex; }
.flex-wrap { flex-wrap: wrap; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.flex-1 { flex: 1; }
.w-full { width: 100%; }

/* ── Responsive ──────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .sidebar      { display: none; }
  .mobile-topbar{ display: flex; }
  .bottom-nav   { display: block; }
  .main-content { padding-bottom: calc(64px + env(safe-area-inset-bottom)); }
  .hero-title   { font-size: clamp(2rem, 10vw, 3rem); }
  .container    { padding: 0 16px; }
  .feature-grid { grid-template-columns: 1fr 1fr; }
  .toast        { right: 16px; bottom: calc(72px + env(safe-area-inset-bottom)); }
}

@media (max-width: 374px) {
  .feature-grid { grid-template-columns: 1fr; }
  .bnav-item    { min-height: 52px; }
}
```

- [ ] **Step 3: Verify no syntax errors by opening any page in browser**

Open `http://127.0.0.1:8000/app/index.html` and confirm: cream background, no console errors. If the server isn't running, start it first:
```
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- [ ] **Step 4: Commit**

```bash
git add frontend/styles.css
git commit -m "feat: rewrite styles.css — Creatorly token system, dual-mode, bottom nav"
```

---

## Task 2: Update `frontend/translate.html`

**Files:**
- Modify: `frontend/translate.html` (strip inline styles, use shared classes, add bottom nav + theme toggle)

The translate page is the highest-priority page. It has 2,001 lines; most of the bulk is its `<style>` block which is being replaced.

- [ ] **Step 1: Read the current `<head>` and `<style>` block**

```bash
head -n 80 frontend/translate.html
```

Note what Google Fonts link is currently loaded and what CSS variables are defined inline.

- [ ] **Step 2: Replace the `<head>` block**

The `<head>` should look exactly like this (replace everything from `<!DOCTYPE html>` through `</style>`):

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Translate — Luganda AI Studio</title>
  <!-- Flash prevention: set theme before first paint -->
  <script>(function(){const t=localStorage.getItem('theme');if(t==='dark')document.documentElement.setAttribute('data-theme','dark');})()</script>
  <!-- PWA -->
  <link rel="manifest" href="/app/manifest.json" />
  <meta name="theme-color" content="#E8E6DE" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;600;700;800&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/app/styles.css" />
</head>
```

- [ ] **Step 3: Replace the `<body>` opening and sidebar with the new shell**

Directly after `<body>`, replace whatever nav/sidebar exists with:

```html
<body>
<div class="app-shell">

  <!-- Sidebar (desktop) -->
  <aside class="sidebar">
    <div class="sidebar-brand">Luganda <span>AI</span></div>
    <nav class="sidebar-nav">
      <a href="index.html"     class="sidebar-link">⌂ Home</a>
      <a href="translate.html" class="sidebar-link active">⇄ Translate</a>
      <a href="search.html"    class="sidebar-link">◎ Search</a>
      <a href="teach.html"     class="sidebar-link">📖 Teach</a>
      <a href="reviews.html"   class="sidebar-link">★ Reviews</a>
      <a href="admin.html"     class="sidebar-link">⚙ Admin</a>
    </nav>
    <div class="sidebar-footer">
      <div class="theme-pill">
        <button class="theme-pill-btn" id="btnLight" onclick="setTheme('light')">☀ Light</button>
        <button class="theme-pill-btn" id="btnDark"  onclick="setTheme('dark')">🌙 Dark</button>
      </div>
      <div class="sidebar-version">v1.0 · Luganda AI Studio</div>
    </div>
  </aside>

  <!-- Mobile topbar -->
  <header class="mobile-topbar">
    <span class="mobile-topbar-title">Translate</span>
    <button class="theme-icon-btn" id="mobileThemeBtn" onclick="toggleTheme()" title="Toggle theme">☀</button>
  </header>

  <!-- Main content -->
  <main class="main-content">
    <div class="container" style="padding-top:32px; padding-bottom:32px;">
```

- [ ] **Step 4: Update key component classes inside the page body**

Find and replace these class/style patterns throughout the body (do not change any JS logic):

| Old pattern | Replace with |
|---|---|
| Any hardcoded `style="background:#..."` on cards | `class="card"` |
| Translate button: `style="background:var(--green-mid)..."` | `class="btn-primary"` |
| Direction buttons (`en_to_lg` / `lg_to_en`) | `class="dir-btn"` / `class="dir-btn active"` inside a `<div class="direction-toggle">` |
| Feedback buttons (Correct/Wrong/Review) | `class="feedback-btn"` |
| The textarea for input | add `class="input-field"` |
| Confidence/match-type chips | `class="chip chip-success"` / `chip-amber` / `chip-red` / `chip-neutral` |
| TTS speaker button | `class="tts-btn"` |
| Session history export button | `class="btn-secondary"` |

- [ ] **Step 5: Close the body with bottom nav**

Before `</body>`, add:

```html
    </div><!-- /.container -->
  </main><!-- /.main-content -->
</div><!-- /.app-shell -->

<!-- Bottom nav (mobile) -->
<nav class="bottom-nav">
  <div class="bottom-nav-inner">
    <a href="index.html"     class="bnav-item"        data-page="index"><span class="bnav-icon">⌂</span><span class="bnav-label">Home</span></a>
    <a href="translate.html" class="bnav-item active"  data-page="translate"><span class="bnav-icon">⇄</span><span class="bnav-label">Translate</span></a>
    <a href="search.html"    class="bnav-item"        data-page="search"><span class="bnav-icon">◎</span><span class="bnav-label">Search</span></a>
    <a href="teach.html"     class="bnav-item"        data-page="teach"><span class="bnav-icon">📖</span><span class="bnav-label">Teach</span></a>
  </div>
</nav>

<script>
function setTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  localStorage.setItem('theme', t);
  updateThemeUI();
}
function toggleTheme() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  setTheme(isDark ? 'light' : 'dark');
}
function updateThemeUI() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const btnLight = document.getElementById('btnLight');
  const btnDark  = document.getElementById('btnDark');
  const mobileBtn = document.getElementById('mobileThemeBtn');
  if (btnLight) btnLight.classList.toggle('active', !isDark);
  if (btnDark)  btnDark.classList.toggle('active', isDark);
  if (mobileBtn) mobileBtn.textContent = isDark ? '☀' : '🌙';
}
updateThemeUI();
</script>
</body>
</html>
```

- [ ] **Step 6: Verify in browser**

Open `http://127.0.0.1:8000/app/translate.html`. Check:
- Page has cream background (light) or dark background (dark) depending on stored preference
- Sidebar visible on desktop, bottom nav visible on mobile (resize window)
- Theme pill in sidebar switches modes without flash on reload
- Translation still works end-to-end (type text, click translate, see result)
- TTS 🔊 button still fires
- Feedback buttons still post to API

- [ ] **Step 7: Commit**

```bash
git add frontend/translate.html
git commit -m "feat: translate.html — Creatorly redesign, dual-mode, bottom nav"
```

---

## Task 3: Update `frontend/teach.html`

**Files:**
- Modify: `frontend/teach.html` (strip inline styles, shared classes, bottom nav)

- [ ] **Step 1: Replace `<head>` block**

Same as Task 2 Step 2, but change title to `Teach — Luganda AI Studio` and `theme-color` to `#E8E6DE`.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Teach — Luganda AI Studio</title>
  <script>(function(){const t=localStorage.getItem('theme');if(t==='dark')document.documentElement.setAttribute('data-theme','dark');})()</script>
  <link rel="manifest" href="/app/manifest.json" />
  <meta name="theme-color" content="#E8E6DE" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;600;700;800&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/app/styles.css" />
</head>
```

- [ ] **Step 2: Replace `<body>` opening with app-shell + sidebar**

```html
<body>
<div class="app-shell">
  <aside class="sidebar">
    <div class="sidebar-brand">Luganda <span>AI</span></div>
    <nav class="sidebar-nav">
      <a href="index.html"     class="sidebar-link">⌂ Home</a>
      <a href="translate.html" class="sidebar-link">⇄ Translate</a>
      <a href="search.html"    class="sidebar-link">◎ Search</a>
      <a href="teach.html"     class="sidebar-link active">📖 Teach</a>
      <a href="reviews.html"   class="sidebar-link">★ Reviews</a>
      <a href="admin.html"     class="sidebar-link">⚙ Admin</a>
    </nav>
    <div class="sidebar-footer">
      <div class="theme-pill">
        <button class="theme-pill-btn" id="btnLight" onclick="setTheme('light')">☀ Light</button>
        <button class="theme-pill-btn" id="btnDark"  onclick="setTheme('dark')">🌙 Dark</button>
      </div>
      <div class="sidebar-version">v1.0 · Luganda AI Studio</div>
    </div>
  </aside>
  <header class="mobile-topbar">
    <span class="mobile-topbar-title">Teach</span>
    <button class="theme-icon-btn" id="mobileThemeBtn" onclick="toggleTheme()">☀</button>
  </header>
  <main class="main-content">
    <div class="container" style="padding-top:32px; padding-bottom:32px;">
```

- [ ] **Step 3: Update component classes in page body**

| Old pattern | Replace with |
|---|---|
| Flash card container with hardcoded bg | `class="card"` |
| "Show Answer" / "Next Card" buttons | `class="btn-primary"` |
| "I knew it" / "Review again" quiz buttons | `class="btn-primary"` / `class="btn-secondary"` |
| Collection filter buttons | `class="btn-secondary"` |
| TTS button | `class="tts-btn"` |
| Score/progress chips | `class="chip chip-success"` / `chip-amber` |

- [ ] **Step 4: Close body with bottom nav and theme script**

```html
    </div>
  </main>
</div>

<nav class="bottom-nav">
  <div class="bottom-nav-inner">
    <a href="index.html"     class="bnav-item"       data-page="index"><span class="bnav-icon">⌂</span><span class="bnav-label">Home</span></a>
    <a href="translate.html" class="bnav-item"       data-page="translate"><span class="bnav-icon">⇄</span><span class="bnav-label">Translate</span></a>
    <a href="search.html"    class="bnav-item"       data-page="search"><span class="bnav-icon">◎</span><span class="bnav-label">Search</span></a>
    <a href="teach.html"     class="bnav-item active" data-page="teach"><span class="bnav-icon">📖</span><span class="bnav-label">Teach</span></a>
  </div>
</nav>

<script>
function setTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  localStorage.setItem('theme', t);
  updateThemeUI();
}
function toggleTheme() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  setTheme(isDark ? 'light' : 'dark');
}
function updateThemeUI() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  document.getElementById('btnLight')?.classList.toggle('active', !isDark);
  document.getElementById('btnDark')?.classList.toggle('active', isDark);
  const mb = document.getElementById('mobileThemeBtn');
  if (mb) mb.textContent = isDark ? '☀' : '🌙';
}
updateThemeUI();
</script>
</body>
</html>
```

- [ ] **Step 5: Verify in browser**

Open `http://127.0.0.1:8000/app/teach.html`. Check:
- Flash cards render with `--bg-card` background
- Mode toggle (flash card / quiz) still works
- TTS 🔊 button still plays audio
- Theme toggle persists across navigation to other pages

- [ ] **Step 6: Commit**

```bash
git add frontend/teach.html
git commit -m "feat: teach.html — Creatorly redesign, dual-mode, bottom nav"
```

---

## Task 4: Update `frontend/search.html`

**Files:**
- Modify: `frontend/search.html` (strip inline styles, shared classes, bottom nav)

- [ ] **Step 1: Replace `<head>` block**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Search — Luganda AI Studio</title>
  <script>(function(){const t=localStorage.getItem('theme');if(t==='dark')document.documentElement.setAttribute('data-theme','dark');})()</script>
  <link rel="manifest" href="/app/manifest.json" />
  <meta name="theme-color" content="#E8E6DE" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;600;700;800&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/app/styles.css" />
</head>
```

- [ ] **Step 2: Replace `<body>` opening with app-shell + sidebar**

```html
<body>
<div class="app-shell">
  <aside class="sidebar">
    <div class="sidebar-brand">Luganda <span>AI</span></div>
    <nav class="sidebar-nav">
      <a href="index.html"     class="sidebar-link">⌂ Home</a>
      <a href="translate.html" class="sidebar-link">⇄ Translate</a>
      <a href="search.html"    class="sidebar-link active">◎ Search</a>
      <a href="teach.html"     class="sidebar-link">📖 Teach</a>
      <a href="reviews.html"   class="sidebar-link">★ Reviews</a>
      <a href="admin.html"     class="sidebar-link">⚙ Admin</a>
    </nav>
    <div class="sidebar-footer">
      <div class="theme-pill">
        <button class="theme-pill-btn" id="btnLight" onclick="setTheme('light')">☀ Light</button>
        <button class="theme-pill-btn" id="btnDark"  onclick="setTheme('dark')">🌙 Dark</button>
      </div>
      <div class="sidebar-version">v1.0 · Luganda AI Studio</div>
    </div>
  </aside>
  <header class="mobile-topbar">
    <span class="mobile-topbar-title">Search</span>
    <button class="theme-icon-btn" id="mobileThemeBtn" onclick="toggleTheme()">☀</button>
  </header>
  <main class="main-content">
    <div class="container" style="padding-top:32px; padding-bottom:32px;">
```

- [ ] **Step 3: Update component classes**

| Old pattern | Replace with |
|---|---|
| Search input | `class="input-field"` |
| Search button | `class="btn-primary"` |
| Collection filter buttons | `class="btn-secondary"` / `class="btn-secondary"` with active state inline |
| Result cards | `class="result-card"` |
| Score chips | `class="chip chip-success"` / `chip-amber` / `chip-red` |

- [ ] **Step 4: Close body with bottom nav and theme script**

```html
    </div>
  </main>
</div>

<nav class="bottom-nav">
  <div class="bottom-nav-inner">
    <a href="index.html"     class="bnav-item"        data-page="index"><span class="bnav-icon">⌂</span><span class="bnav-label">Home</span></a>
    <a href="translate.html" class="bnav-item"        data-page="translate"><span class="bnav-icon">⇄</span><span class="bnav-label">Translate</span></a>
    <a href="search.html"    class="bnav-item active"  data-page="search"><span class="bnav-icon">◎</span><span class="bnav-label">Search</span></a>
    <a href="teach.html"     class="bnav-item"        data-page="teach"><span class="bnav-icon">📖</span><span class="bnav-label">Teach</span></a>
  </div>
</nav>

<script>
function setTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  localStorage.setItem('theme', t);
  updateThemeUI();
}
function toggleTheme() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  setTheme(isDark ? 'light' : 'dark');
}
function updateThemeUI() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  document.getElementById('btnLight')?.classList.toggle('active', !isDark);
  document.getElementById('btnDark')?.classList.toggle('active', isDark);
  const mb = document.getElementById('mobileThemeBtn');
  if (mb) mb.textContent = isDark ? '☀' : '🌙';
}
updateThemeUI();
</script>
</body>
</html>
```

- [ ] **Step 5: Verify in browser**

Open `http://127.0.0.1:8000/app/search.html`. Check:
- Search bar accepts input, submit triggers API call to `/api/v1/knowledge/search`
- Results render with score chips
- Collection filter buttons highlight the active collection

- [ ] **Step 6: Commit**

```bash
git add frontend/search.html
git commit -m "feat: search.html — Creatorly redesign, dual-mode, bottom nav"
```

---

## Task 5: Restructure `frontend/index.html`

**Files:**
- Modify: `frontend/index.html` (full restructure — hero, feature cards, theme pill, secondary links)

This is the largest structural change. The old page has a feature grid but uses dark/green palette and Fraunces font.

- [ ] **Step 1: Replace `<head>` block**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Luganda AI Studio</title>
  <script>(function(){const t=localStorage.getItem('theme');if(t==='dark')document.documentElement.setAttribute('data-theme','dark');})()</script>
  <link rel="manifest" href="/app/manifest.json" />
  <meta name="theme-color" content="#E8E6DE" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="default" />
  <meta name="apple-mobile-web-app-title" content="Luganda AI" />
  <link rel="apple-touch-icon" href="/app/icons/icon-192.svg" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;600;700;800&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/app/styles.css" />
</head>
```

- [ ] **Step 2: Replace full `<body>` with new structure**

Replace everything from `<body>` to `</body>` with:

```html
<body>
<div class="app-shell">

  <!-- Sidebar (desktop) -->
  <aside class="sidebar">
    <div class="sidebar-brand">Luganda <span>AI</span></div>
    <nav class="sidebar-nav">
      <a href="index.html"     class="sidebar-link active">⌂ Home</a>
      <a href="translate.html" class="sidebar-link">⇄ Translate</a>
      <a href="search.html"    class="sidebar-link">◎ Search</a>
      <a href="teach.html"     class="sidebar-link">📖 Teach</a>
      <a href="reviews.html"   class="sidebar-link">★ Reviews</a>
      <a href="admin.html"     class="sidebar-link">⚙ Admin</a>
    </nav>
    <div class="sidebar-footer">
      <div class="theme-pill">
        <button class="theme-pill-btn" id="btnLight" onclick="setTheme('light')">☀ Light</button>
        <button class="theme-pill-btn" id="btnDark"  onclick="setTheme('dark')">🌙 Dark</button>
      </div>
      <div class="sidebar-version">v1.0 · Luganda AI Studio</div>
    </div>
  </aside>

  <!-- Mobile topbar -->
  <header class="mobile-topbar">
    <span class="mobile-topbar-title">Luganda AI Studio</span>
    <button class="theme-icon-btn" id="mobileThemeBtn" onclick="toggleTheme()">☀</button>
  </header>

  <!-- Main content -->
  <main class="main-content">
    <div class="container">

      <!-- Hero -->
      <section class="hero">
        <div class="hero-kicker">Luganda AI Studio</div>
        <h1 class="hero-title">
          Translate.<br>
          Learn.<br>
          <span class="hero-underline">Communicate.</span>
        </h1>
        <p class="hero-desc">AI-powered tools for the Luganda language — built to run on your machine.</p>
        <div class="flex gap-12 flex-wrap mt-8">
          <a href="translate.html" class="btn-primary">Start Translating →</a>
          <div class="theme-pill" id="heroPill" style="align-self:center;">
            <button class="theme-pill-btn" id="heroLight" onclick="setTheme('light')">☀ Light</button>
            <button class="theme-pill-btn" id="heroDark"  onclick="setTheme('dark')">🌙 Dark</button>
          </div>
        </div>
      </section>

      <!-- Stats -->
      <div class="stats-row" id="statsRow">
        <div class="stat-item"><span class="stat-value" id="statVocab">—</span><span class="stat-label">Vocabulary pairs</span></div>
        <div class="stat-item"><span class="stat-value" id="statSentences">—</span><span class="stat-label">Sentence pairs</span></div>
        <div class="stat-item"><span class="stat-value" id="statGrammar">—</span><span class="stat-label">Grammar notes</span></div>
        <div class="stat-item"><span class="stat-value" id="statProverbs">—</span><span class="stat-label">Proverbs</span></div>
      </div>

      <!-- Feature grid -->
      <div class="feature-grid mt-24">
        <a href="translate.html" class="feature-card">
          <div class="feature-card-icon">⇄</div>
          <div class="feature-card-title">Translate</div>
          <div class="feature-card-desc">Luganda ↔ English with confidence scoring and neural fallback.</div>
        </a>
        <a href="search.html" class="feature-card">
          <div class="feature-card-icon">◎</div>
          <div class="feature-card-title">Search</div>
          <div class="feature-card-desc">Semantic search across vocabulary, sentences, grammar and proverbs.</div>
        </a>
        <a href="teach.html" class="feature-card">
          <div class="feature-card-icon">📖</div>
          <div class="feature-card-title">Teach</div>
          <div class="feature-card-desc">Flash cards and quiz mode to build Luganda vocabulary fast.</div>
        </a>
        <a href="reviews.html" class="feature-card">
          <div class="feature-card-icon">★</div>
          <div class="feature-card-title">Reviews</div>
          <div class="feature-card-desc">Browse user feedback and correction history.</div>
        </a>
      </div>

      <!-- More / secondary links -->
      <div class="more-section mb-24">
        <div class="more-title">More</div>
        <div class="more-links">
          <a href="admin.html"  class="more-link">⚙ Admin Dashboard</a>
          <a href="/docs"       class="more-link">📄 API Docs</a>
        </div>
      </div>

    </div><!-- /.container -->
  </main><!-- /.main-content -->
</div><!-- /.app-shell -->

<!-- Bottom nav (mobile) -->
<nav class="bottom-nav">
  <div class="bottom-nav-inner">
    <a href="index.html"     class="bnav-item active"  data-page="index"><span class="bnav-icon">⌂</span><span class="bnav-label">Home</span></a>
    <a href="translate.html" class="bnav-item"         data-page="translate"><span class="bnav-icon">⇄</span><span class="bnav-label">Translate</span></a>
    <a href="search.html"    class="bnav-item"         data-page="search"><span class="bnav-icon">◎</span><span class="bnav-label">Search</span></a>
    <a href="teach.html"     class="bnav-item"         data-page="teach"><span class="bnav-icon">📖</span><span class="bnav-label">Teach</span></a>
  </div>
</nav>

<script>
function setTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  localStorage.setItem('theme', t);
  updateThemeUI();
}
function toggleTheme() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  setTheme(isDark ? 'light' : 'dark');
}
function updateThemeUI() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  ['btnLight','heroLight'].forEach(id => document.getElementById(id)?.classList.toggle('active', !isDark));
  ['btnDark','heroDark'].forEach(id   => document.getElementById(id)?.classList.toggle('active', isDark));
  const mb = document.getElementById('mobileThemeBtn');
  if (mb) mb.textContent = isDark ? '☀' : '🌙';
}
updateThemeUI();

// Load stats from /api/v1/knowledge/stats
fetch('/api/v1/knowledge/stats')
  .then(r => r.json())
  .then(d => {
    document.getElementById('statVocab').textContent     = (d.vocabulary    ?? '—').toLocaleString();
    document.getElementById('statSentences').textContent = (d.sentences     ?? '—').toLocaleString();
    document.getElementById('statGrammar').textContent   = (d.grammar       ?? '—').toLocaleString();
    document.getElementById('statProverbs').textContent  = (d.proverbs      ?? '—').toLocaleString();
  })
  .catch(() => {});
</script>
</body>
</html>
```

- [ ] **Step 3: Verify in browser**

Open `http://127.0.0.1:8000/app/index.html`. Check:
- Cream background in light mode
- Hero title renders in Figtree 800, `clamp(2.4rem…4rem)` responsive size
- "Communicate." has lime underline
- Feature cards hover with lime left border
- Stats row populates with live data from `/api/v1/knowledge/stats`
- Theme pill (hero) and sidebar pill both switch mode and stay in sync
- Mobile: bottom nav appears, sidebar hidden (resize window to 375px)

- [ ] **Step 4: Commit**

```bash
git add frontend/index.html
git commit -m "feat: index.html — hero, feature cards, theme pill, Creatorly redesign"
```

---

## Task 6: Token sweep — `frontend/admin.html` + `frontend/reviews.html`

**Files:**
- Modify: `frontend/admin.html`
- Modify: `frontend/reviews.html`

These pages have minimal structural change — just replace the `<head>` with the new font/stylesheet, add the app-shell wrapper, sidebar, mobile topbar, bottom nav, and theme script. Internal card/button/chip content should already pick up shared classes if they were using class names; any hardcoded colour `style=` attributes should be removed and replaced with the nearest shared class.

- [ ] **Step 1: Update `frontend/admin.html` `<head>`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Admin — Luganda AI Studio</title>
  <script>(function(){const t=localStorage.getItem('theme');if(t==='dark')document.documentElement.setAttribute('data-theme','dark');})()</script>
  <link rel="manifest" href="/app/manifest.json" />
  <meta name="theme-color" content="#E8E6DE" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;600;700;800&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/app/styles.css" />
</head>
```

- [ ] **Step 2: Wrap `admin.html` body in app-shell with sidebar (active = Admin) + bottom nav**

Use the same sidebar HTML as Tasks 2–5. Active link is `admin.html`. Bottom nav has no active tab (admin is a secondary page). Add theme script at bottom.

```html
<!-- sidebar active link: admin.html -->
<!-- bottom nav: no .active class on any bnav-item -->
```

- [ ] **Step 3: Repeat Steps 1–2 for `frontend/reviews.html`**

Same pattern. Title: `Reviews — Luganda AI Studio`. Active sidebar link: `reviews.html`. No active bottom nav tab.

- [ ] **Step 4: Verify both pages in browser**

Open `/app/admin.html` and `/app/reviews.html`. Verify:
- Both render with new tokens (cream or dark depending on stored theme)
- No broken layout or missing content
- Admin cards (system health, collection counts, pipeline status) still load data from API
- Reviews table still loads and filters feedback

- [ ] **Step 5: Commit**

```bash
git add frontend/admin.html frontend/reviews.html
git commit -m "feat: admin + reviews — Creatorly token sweep, bottom nav, dual-mode"
```

---

## Self-Review Against Spec

| Spec requirement | Covered in task |
|---|---|
| Light mode: `#E8E6DE` bg, `#1C2B1A` text, `#CADF3E` accent | Task 1 — `:root` tokens |
| Dark mode: `#0D1117` bg, `#E6EDF3` text, `#CADF3E` accent | Task 1 — `[data-theme="dark"]` |
| Flash prevention script | Tasks 2–6 — `<script>` in `<head>` |
| Figtree 800 display font | Tasks 1–6 — `<link>` + `--font-display` |
| DM Sans body font | Tasks 1–6 — `--font-body` unchanged |
| Lime pill button `border-radius: 50px` | Task 1 — `.btn-primary` |
| Sidebar: lime `border-left` on active link | Task 1 — `.sidebar-link.active` |
| Sidebar: theme pill above version tag | Tasks 2–6 — `.sidebar-footer` |
| Mobile: 4-tab bottom bar replaces hamburger | Task 1 — `.bottom-nav`, Tasks 2–6 — HTML |
| Mobile topbar: title + theme icon only | Task 1 — `.mobile-topbar`, Tasks 2–6 |
| Theme pill on home page hero | Task 5 — `#heroPill` |
| Secondary links (Reviews, Admin) on Home "More" section | Task 5 — `.more-section` |
| iOS safe area padding on bottom nav | Task 1 — `env(safe-area-inset-bottom)` |
| 48px min touch targets | Task 1 — `.btn-primary`, `.bnav-item` |
| Hero: Figtree, `clamp(2.4rem…4rem)`, lime underline on "Communicate." | Task 5 |
| Feature cards: lime left border on hover | Task 1 — `.feature-card:hover` |
| Priority order: translate → teach → search → index → admin | Tasks 2→3→4→5→6 |
| Backend/JS logic untouched | Tasks 2–6 — only `<head>`, shell, and class names changed |
| `chat.html` not in scope | Not included — correct |
