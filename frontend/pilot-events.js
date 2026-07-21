// frontend/pilot-events.js — anonymous pilot event sender.
// Events carry ONLY curated identifiers: slugs, curated ids/keys, tool names,
// theme names. Never user input, typed text, search queries, or translation
// content. Invalid targets are REJECTED, never sanitized into a stored value.
'use strict';

const EVENT_NAMES = [
  'onboarding_started', 'onboarding_completed',
  'home_destination_opened', 'collection_opened', 'item_opened',
  'lesson_started', 'lesson_completed',
  'tool_opened',
  'correction_started', 'correction_submitted',
  'theme_changed',
];

// Same identifier grammar the backend enforces.
const TARGET_RE = /^[A-Za-z0-9_.:-]*$/;

function buildEvent(session, event, target) {
  if (!EVENT_NAMES.includes(event)) return null;
  const t = (target === undefined || target === null) ? '' : String(target);
  if (t.length > 64 || !TARGET_RE.test(t)) return null; // reject, never transform
  return { session, event, target: t };
}

function uuid4() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID();
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function ensureSession() {
  let s = localStorage.getItem('pilot.session');
  if (!s) {
    s = uuid4();
    localStorage.setItem('pilot.session', s);
  }
  return s;
}

// Fire-and-forget. Analytics must never break or block a learner journey.
function sendEvent(event, target) {
  try {
    const payload = buildEvent(ensureSession(), event, target);
    if (!payload) return;
    fetch('/api/v1/events', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      keepalive: true,
    }).catch(() => {});
  } catch (e) { /* swallow — never surface analytics errors to the learner */ }
}

if (typeof window !== 'undefined') {
  window.sendEvent = sendEvent;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { EVENT_NAMES, buildEvent };
}
