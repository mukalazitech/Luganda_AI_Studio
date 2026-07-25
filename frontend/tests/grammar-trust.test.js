const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '..', 'grammar.html'), 'utf8');

test('grammar cards only claim source review when verification metadata exists', () => {
  assert.match(html, /section\.verified\s*\?\s*'Source reviewed'\s*:\s*'Needs language review'/);
  assert.match(html, /grammar-trust/);
  assert.match(html, /verification_notes/);
});

test('grammar trust rendering exposes source IDs without changing lesson text', () => {
  assert.match(html, /section\.source_ids/);
  assert.match(html, /Sources?:/);
});
