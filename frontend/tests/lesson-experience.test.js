const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '..', 'learn.html'), 'utf8');
const js = fs.readFileSync(path.join(__dirname, '..', 'learn.js'), 'utf8');

test('lesson steps include a Listen control backed by cancellable TTS', () => {
  assert.match(js, /listenButton\(entry\.luganda\)/);
  assert.match(js, /new AbortController\(\)/);
  assert.match(js, /requestId\s*!==\s*ttsRequestId/);
  assert.match(js, /Audio unavailable/);
});

test('lesson completion names the lesson and shows score and XP', () => {
  assert.match(html, /id="summary-title"/);
  assert.match(html, /id="summary-score"/);
  assert.match(html, /id="summary-xp"/);
  assert.match(js, /summary-title/);
  assert.match(js, /earnedXp\(score\)/);
});

test('lesson completion offers review and a next lesson', () => {
  assert.match(html, /id="summary-review"/);
  assert.match(html, /id="summary-next"/);
  assert.match(js, /nextLesson\(state\.lessons,\s*lesson\.id\)/);
});
