const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.join(__dirname, '..', '..');
const lessons = JSON.parse(fs.readFileSync(path.join(ROOT, 'datasets', 'lessons', 'beginner_path.json'), 'utf8'));

function allSentenceIds() {
  const ids = new Set();
  for (const f of fs.readdirSync(path.join(ROOT, 'datasets', 'sentences'))) {
    const d = JSON.parse(fs.readFileSync(path.join(ROOT, 'datasets', 'sentences', f), 'utf8'));
    for (const e of d.entries) ids.add(e.id);
  }
  return ids;
}
function allVocabKeys() {
  const keys = new Set();
  for (const f of fs.readdirSync(path.join(ROOT, 'datasets', 'vocabulary'))) {
    const d = JSON.parse(fs.readFileSync(path.join(ROOT, 'datasets', 'vocabulary', f), 'utf8'));
    for (const e of d.entries) keys.add(`${e.category}:${e.luganda}`);
  }
  return keys;
}

test('every lesson step references an existing dataset entry', () => {
  const sids = allSentenceIds(), vkeys = allVocabKeys();
  for (const lesson of lessons.lessons) {
    assert.ok(lesson.id && lesson.title && Array.isArray(lesson.steps) && lesson.steps.length > 0);
    for (const step of lesson.steps) {
      if (step.ref_type === 'sentence') assert.ok(sids.has(step.ref), `unknown sentence ${step.ref} in ${lesson.id}`);
      else if (step.ref_type === 'vocabulary') assert.ok(vkeys.has(step.ref), `unknown vocab ${step.ref} in ${lesson.id}`);
      else assert.fail(`unknown ref_type ${step.ref_type}`);
    }
  }
});

test('no lesson step carries its own luganda/english text (no invented content)', () => {
  for (const lesson of lessons.lessons)
    for (const step of lesson.steps) {
      assert.strictEqual(step.luganda, undefined);
      assert.strictEqual(step.english, undefined);
    }
});