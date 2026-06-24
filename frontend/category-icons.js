/* category-icons.js — maps a word's semantic category to an emoji cue.
   The 12 categories come from datasets/vocabulary/*.json plus 'greeting'
   from the API fallback set. One emoji per category scales to every word. */

const CATEGORY_ICON = {
  animals:        '🐐',
  food_and_drink: '🍲',
  family:         '👪',
  body_parts:     '✋',
  transport:      '🚲',
  numbers:        '🔢',
  time:           '⏰',
  health:         '❤️‍🩹',
  places:         '🏠',
  clothing:       '👕',
  emotions:       '😊',
  colors:         '🎨',
  greeting:       '👋',
};

const FALLBACK_ICON = '📖';

function categoryIcon(category) {
  if (!category || typeof category !== 'string') return FALLBACK_ICON;
  return CATEGORY_ICON[category.trim().toLowerCase()] || FALLBACK_ICON;
}

function categoryLabel(category) {
  if (!category || typeof category !== 'string') return '';
  const words = category.trim().toLowerCase().replace(/_and_/g, ' & ').replace(/_/g, ' ');
  return words.charAt(0).toUpperCase() + words.slice(1);
}

// Dual export: CommonJS for node:test, global for the browser (matches mascot.js).
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { categoryIcon, categoryLabel, CATEGORY_ICON, FALLBACK_ICON };
}
if (typeof window !== 'undefined') {
  window.categoryIcon = categoryIcon;
  window.categoryLabel = categoryLabel;
}
