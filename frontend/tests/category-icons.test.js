const test = require('node:test');
const assert = require('node:assert');
const { categoryIcon, categoryLabel, CATEGORY_ICON, FALLBACK_ICON } = require('../category-icons.js');

test('maps each known category to its emoji', () => {
  assert.strictEqual(categoryIcon('animals'), '🐐');
  assert.strictEqual(categoryIcon('food_and_drink'), '🍲');
  assert.strictEqual(categoryIcon('colors'), '🎨');
});

test('is case-insensitive and trims input', () => {
  assert.strictEqual(categoryIcon('  ANIMALS '), '🐐');
});

test('falls back for unknown or empty category', () => {
  assert.strictEqual(categoryIcon('zzz'), FALLBACK_ICON);
  assert.strictEqual(categoryIcon(''), FALLBACK_ICON);
  assert.strictEqual(categoryIcon(null), FALLBACK_ICON);
  assert.strictEqual(categoryIcon(undefined), FALLBACK_ICON);
});

test('formats labels: underscores to spaces, _and_ to &, capitalised', () => {
  assert.strictEqual(categoryLabel('food_and_drink'), 'Food & drink');
  assert.strictEqual(categoryLabel('body_parts'), 'Body parts');
  assert.strictEqual(categoryLabel('animals'), 'Animals');
});

test('every category in the map also formats to a non-empty label', () => {
  for (const cat of Object.keys(CATEGORY_ICON)) {
    assert.ok(categoryLabel(cat).length > 0, `${cat} must format to a label`);
  }
});
