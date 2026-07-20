const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const FRONTEND_DIR = path.resolve(__dirname, '..');
const SPRITE_PATH = path.join(FRONTEND_DIR, 'assets', 'icons.svg');
const REQUIRED_IDS = [
  'home', 'translate', 'learn', 'explore', 'proverbs',
  'grammar', 'phrases', 'library', 'search', 'listen',
  'speak', 'chat', 'teach', 'streak', 'xp', 'theme',
  'settings', 'correct', 'back', 'external',
].map((name) => `icon-${name}`);

function readSprite() {
  return fs.readFileSync(SPRITE_PATH, 'utf8');
}

function symbolIds(svg) {
  return [...svg.matchAll(/<symbol\b[^>]*\bid=["']([^"']+)["']/g)]
    .map((match) => match[1]);
}

test('local outline sprite defines the complete 20-icon contract', () => {
  const svg = readSprite();
  const ids = symbolIds(svg);

  assert.deepStrictEqual([...ids].sort(), [...REQUIRED_IDS].sort());
  assert.strictEqual(new Set(ids).size, ids.length, 'symbol IDs must be unique');
  assert.strictEqual((svg.match(/<symbol\b/g) || []).length, REQUIRED_IDS.length);
  assert.match(svg, /<svg\b[^>]*\bstyle=["'][^"']*display:\s*none/);
  assert.strictEqual((svg.match(/<symbol\b[^>]*\bviewBox=["']0 0 24 24["']/g) || []).length, REQUIRED_IDS.length);
  assert.match(svg, /<svg\b[^>]*\bfill=["']none["']/);
  assert.match(svg, /<svg\b[^>]*\bstroke=["']currentColor["']/);
  assert.doesNotMatch(svg, /<script\b|\bon\w+\s*=|(?:href|src)\s*=\s*["'](?:https?:)?\/\//i);
});

test('every SVG use reference in frontend HTML resolves to a local sprite symbol', () => {
  const ids = new Set(symbolIds(readSprite()));
  const htmlFiles = fs.readdirSync(FRONTEND_DIR)
    .filter((name) => name.endsWith('.html'));

  for (const fileName of htmlFiles) {
    const html = fs.readFileSync(path.join(FRONTEND_DIR, fileName), 'utf8');
    const uses = html.matchAll(/<use\b[^>]*\bhref=["']([^"']+)["'][^>]*>/g);

    for (const [, href] of uses) {
      const [assetPath, fragment] = href.split('#');
      assert.ok(fragment, `${fileName}: ${href} must include a symbol fragment`);
      assert.ok(
        assetPath === 'assets/icons.svg' || assetPath === '/app/assets/icons.svg',
        `${fileName}: ${href} must reference the local icon sprite`,
      );
      assert.ok(ids.has(fragment), `${fileName}: ${href} does not resolve to a symbol`);
    }
  }
});
