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

// Per-word overrides for categories where one shared icon would be misleading
// (e.g. every animal showing a goat). Keys are matched as substrings against
// the lowercased English text, longest key first, so "he-goat" beats "goat".
const WORD_ICON_OVERRIDES = {
  animals: [
    ['dog', '🐕'], ['cat', '🐈'], ['goat', '🐐'], ['hen', '🐔'], ['chicken', '🐔'],
    ['cock', '🐓'], ['cow', '🐄'], ['cattle', '🐄'], ['bull', '🐂'], ['pig', '🐖'],
    ['duck', '🦆'], ['turkey', '🦃'], ['rabbit', '🐇'], ['donkey', '🫏'], ['horse', '🐎'],
    ['elephant', '🐘'], ['lion', '🦁'], ['leopard', '🐆'], ['zebra', '🦓'],
    ['giraffe', '🦒'], ['buffalo', '🐃'], ['rhinoceros', '🦏'], ['hippopotamus', '🦛'],
    ['camel', '🐫'], ['monkey', '🐒'], ['chimpanzee', '🐒'], ['baboon', '🐒'],
    ['colobus', '🐒'], ['gorilla', '🦍'], ['civet', '🐈'], ['bushbuck', '🦌'],
    ['antelope', '🦌'], ['crocodile', '🐊'], ['python', '🐍'], ['snake', '🐍'],
    ['lizard', '🦎'], ['frog', '🐸'], ['chameleon', '🦎'], ['rat', '🐀'], ['mouse', '🐁'],
    ['fox', '🦊'], ['jackal', '🦊'], ['ostrich', '🦤'], ['bear', '🐻'],
    ['crane', '🦩'], ['hawk', '🦅'], ['kite', '🦅'], ['eagle', '🦅'], ['owl', '🦉'],
    ['bird', '🐦'], ['bee', '🐝'], ['grasshopper', '🦗'], ['locust', '🦗'],
    ['cockroach', '🪳'], ['termite', '🐜'], ['ant', '🐜'], ['housefly', '🪰'], ['fly', '🪰'],
  ],
};

function wordIcon(english, category) {
  const cat = (category || '').trim().toLowerCase();
  const overrides = WORD_ICON_OVERRIDES[cat];
  if (overrides && typeof english === 'string' && english.trim()) {
    const text = english.toLowerCase();
    let best = null;
    for (const [key, icon] of overrides) {
      if (text.includes(key) && (!best || key.length > best[0].length)) {
        best = [key, icon];
      }
    }
    if (best) return best[1];
  }
  return categoryIcon(cat);
}

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
  module.exports = { categoryIcon, categoryLabel, wordIcon, CATEGORY_ICON, FALLBACK_ICON };
}
if (typeof window !== 'undefined') {
  window.categoryIcon = categoryIcon;
  window.categoryLabel = categoryLabel;
  window.wordIcon = wordIcon;
}
