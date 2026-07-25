const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const frontendDir = path.resolve(__dirname, '..');
const translate = fs.readFileSync(path.join(frontendDir, 'translate.html'), 'utf8');
const search = fs.readFileSync(path.join(frontendDir, 'search.html'), 'utf8');

test('Translate exposes distinct library, possible, AI and not-found trust states', () => {
  assert.match(translate, /id="resultTrust"/);
  assert.match(translate, /Found in the reviewed library/);
  assert.match(translate, /Possible match — please confirm/);
  assert.match(translate, /AI-generated; may need review/);
  assert.match(translate, /stateNotFound/);
  assert.match(translate, /function renderTrustState\(/);
});

test('Translate explains match type, confidence and source without percentage-only trust', () => {
  assert.match(translate, /matched_source_file/);
  assert.match(translate, /match_type/);
  assert.match(translate, /confidence/);
  assert.match(translate, /resultTrustMeta/);
});

test('Search renders collection, match reason and source tier', () => {
  assert.match(search, /match_reason/);
  assert.match(search, /trust_tier/);
  assert.match(search, /function matchReasonLabel\(/);
  assert.match(search, /result-item-footer/);
});
