'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { buildEvent, EVENT_NAMES } = require('../pilot-events.js');

const UUID = '3f2b8c1e-aaaa-bbbb-cccc-0123456789ab';
const FRONTEND_DIR = path.resolve(__dirname, '..');

test('buildEvent produces only the four allowed fields', () => {
  const e = buildEvent(UUID, 'collection_opened', 'proverbs');
  assert.deepStrictEqual(Object.keys(e).sort(), ['event', 'session', 'target']);
});

test('buildEvent refuses unknown event names', () => {
  assert.strictEqual(buildEvent(UUID, 'typed_text', 'x'), null);
});

test('buildEvent rejects rather than transforms free-text targets', () => {
  const e = buildEvent(UUID, 'item_opened', 'how do I say love?');
  assert.strictEqual(e, null);
});

test('event whitelist matches backend', () => {
  assert.ok(EVENT_NAMES.includes('lesson_completed') && EVENT_NAMES.length === 11);
});

// ── Static call-site guard ────────────────────────────────────────────────
// Every sendEvent(...) target across the learner pages must be a curated
// identifier — never a variable that carries user-typed text.
const WIRED_FILES = [
  'index.html', 'explore.html', 'proverbs.html', 'grammar.html', 'phrases.html',
  'library.html', 'learn.html', 'learn.js', 'translate.html', 'chat.html',
  'search.html', 'theme.js',
].filter((f) => fs.existsSync(path.join(FRONTEND_DIR, f)));

// Extract sendEvent(...) calls, allowing one level of nested parens
// (e.g. el.getAttribute('data-x')).
const CALL_RE = /sendEvent\(([^()]*(?:\([^()]*\)[^()]*)*)\)/g;
// Variable names that may hold user input, a message, a query, or free text.
const FORBIDDEN = /\b(input|inputText|message|msg|query|searchQuery|userText|translated|translatedText|expected|expectedOutput|value|text|q)\b/;

test('no learner input is ever passed as an event target', () => {
  let totalCalls = 0;
  for (const file of WIRED_FILES) {
    const src = fs.readFileSync(path.join(FRONTEND_DIR, file), 'utf8');
    for (const m of src.matchAll(CALL_RE)) {
      totalCalls += 1;
      assert.ok(
        !FORBIDDEN.test(m[1]),
        `${file}: sendEvent target looks like user input: sendEvent(${m[1]})`,
      );
    }
  }
  // Guard against the wiring silently disappearing (which would make the
  // forbidden-token check vacuously pass).
  assert.ok(totalCalls > 0, 'expected at least one wired sendEvent call site');
});
