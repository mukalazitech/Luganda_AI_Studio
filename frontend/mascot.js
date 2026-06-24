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
