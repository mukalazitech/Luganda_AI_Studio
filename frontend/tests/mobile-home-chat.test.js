const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
const css = fs.readFileSync(path.join(root, 'styles.css'), 'utf8');
const home = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const chat = fs.readFileSync(path.join(root, 'chat.html'), 'utf8');

test('mobile theme control has a 44px touch target', () => {
  const block = css.match(/\.theme-icon-btn\s*\{[\s\S]*?\}/)?.[0] || '';
  assert.match(block, /width:\s*44px/);
  assert.match(block, /height:\s*44px/);
});

test('home keeps direct routes to the pilot core features', () => {
  for (const href of ['learn.html', 'translate.html', 'proverbs.html', 'grammar.html', 'phrases.html', 'library.html']) {
    assert.ok(home.includes(`href="${href}"`), `missing ${href}`);
  }
  assert.match(css, /@media \(max-width: 420px\)[\s\S]*?\.home-hero\s*\{[^}]*padding:\s*24px 0 30px/);
});

test('chat is presented as a disabled coming-soon feature', () => {
  assert.match(chat, /Coming soon/);
  assert.match(chat, /Chat is coming soon\./);
  assert.match(chat, /let chatAvailable\s*=\s*false/);
  assert.doesNotMatch(chat, /checkStatus\(\)/);
  assert.match(chat, /id="messageInput"[\s\S]*?disabled/);
  assert.match(chat, /id="sendBtn"[\s\S]*?disabled/);
});
