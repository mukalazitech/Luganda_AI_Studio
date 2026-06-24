const test = require('node:test');
const assert = require('node:assert');
const { categoryIcon, categoryLabel, wordIcon, CATEGORY_ICON, FALLBACK_ICON } = require('../category-icons.js');

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

test('wordIcon gives different animals different icons (no goat-for-everything)', () => {
  assert.strictEqual(wordIcon('Dog', 'animals'), '🐕');
  assert.strictEqual(wordIcon('Goat', 'animals'), '🐐');
  assert.strictEqual(wordIcon('Elephant', 'animals'), '🐘');
  assert.notStrictEqual(wordIcon('Dog', 'animals'), wordIcon('Goat', 'animals'));
});

test('wordIcon matches the longest substring (He-goat beats goat)', () => {
  assert.strictEqual(wordIcon('He-goat / Billy goat', 'animals'), '🐐');
  assert.strictEqual(wordIcon('Hen / Chicken', 'animals'), '🐔');
});

test('wordIcon falls back to the category icon outside the override list / unmatched words', () => {
  assert.strictEqual(wordIcon('Water', 'food_and_drink'), categoryIcon('food_and_drink'));
  assert.strictEqual(wordIcon('Some unmapped animal', 'animals'), categoryIcon('animals'));
});
