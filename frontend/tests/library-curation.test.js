const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const frontendDir = path.resolve(__dirname, '..');
const library = fs.readFileSync(path.join(frontendDir, 'library.html'), 'utf8');
const proverbs = fs.readFileSync(path.join(frontendDir, 'proverbs.html'), 'utf8');

test('Word Library defaults to curated words with an explicit full dictionary mode', () => {
  assert.match(library, /id="curatedMode"/);
  assert.match(library, /id="fullMode"/);
  assert.match(library, /Curated words/);
  assert.match(library, /Full dictionary/);
  assert.match(library, /activeTier='featured'/);
});

test('Word Library paginates results instead of loading a whole corpus category', () => {
  assert.match(library, /const WORD_PAGE_SIZE=/);
  assert.match(library, /slice\(0,visibleWordCount\)/);
  assert.match(library, /id="wordShowMore"/);
});

test('Proverbs limits Featured while keeping every proverb in All search', () => {
  assert.match(proverbs, /const FEATURED_LIMIT=10/);
  assert.match(proverbs, /featuredProverbs=entries\.filter\(item=>item\.tier==='featured'\)\.slice\(0,FEATURED_LIMIT\)/);
  assert.match(proverbs, /allProverbs=entries/);
});
