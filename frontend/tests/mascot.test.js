const test = require('node:test');
const assert = require('node:assert');
const { mascotSrc, MASCOT_STATES, MASCOT_BASE } = require('../mascot.js');

test('resolves a valid character+state to its image path', () => {
  assert.strictEqual(mascotSrc('kintu', 'celebrate'), `${MASCOT_BASE}/kintu/celebrate.png`);
  assert.strictEqual(mascotSrc('nambi', 'explaining'), `${MASCOT_BASE}/nambi/explaining.png`);
});

test('falls back to the character default state when state is unknown', () => {
  // kintu default = first listed state = 'cheering'
  assert.strictEqual(mascotSrc('kintu', 'no-such-state'), `${MASCOT_BASE}/kintu/cheering.png`);
  // nambi default = 'neutral'
  assert.strictEqual(mascotSrc('nambi', 'bogus'), `${MASCOT_BASE}/nambi/neutral.png`);
});

test('returns null for an unknown character so callers can no-op', () => {
  assert.strictEqual(mascotSrc('zzz', 'cheering'), null);
});

test('every character has at least one state (the default)', () => {
  for (const [char, states] of Object.entries(MASCOT_STATES)) {
    assert.ok(Array.isArray(states) && states.length > 0, `${char} must list states`);
  }
});
