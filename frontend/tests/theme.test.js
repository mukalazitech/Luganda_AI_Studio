const test = require('node:test');
const assert = require('node:assert');
const { resolveInitialTheme, THEME_KEY } = require('../theme.js');

test('stored dark or light theme wins over the OS preference', () => {
  assert.strictEqual(resolveInitialTheme('dark', false), 'dark');
  assert.strictEqual(resolveInitialTheme('light', true), 'light');
});

test('OS preference provides the first-visit fallback', () => {
  assert.strictEqual(resolveInitialTheme(null, true), 'dark');
  assert.strictEqual(resolveInitialTheme(null, false), 'light');
});

test('invalid stored values fall back to the OS preference', () => {
  assert.strictEqual(resolveInitialTheme('sepia', true), 'dark');
  assert.strictEqual(resolveInitialTheme('', false), 'light');
});

test('theme storage key is exactly theme', () => {
  assert.strictEqual(THEME_KEY, 'theme');
});
