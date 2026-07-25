const test = require('node:test');
const assert = require('node:assert');
const { nextStep, scoreSession, buildChoices, earnedXp, nextLesson } = require('../learn.js');

test('nextStep advances and terminates', () => {
  assert.strictEqual(nextStep(0, 3), 1);
  assert.strictEqual(nextStep(2, 3), null);
});
test('scoreSession summarises correct/wrong', () => {
  assert.deepStrictEqual(scoreSession([true, true, false]), { seen: 3, correct: 2, wrong: 1 });
});
test('buildChoices returns answer plus distinct distractors', () => {
  const pool = ['a', 'b', 'c', 'd'];
  const choices = buildChoices('a', pool, () => 0.5);
  assert.ok(choices.includes('a'));
  assert.strictEqual(new Set(choices).size, choices.length);
  assert.ok(choices.length >= 2 && choices.length <= 4);
});
test('earnedXp rewards completing steps and correct answers', () => {
  assert.strictEqual(earnedXp({ seen: 4, correct: 3 }), 35);
});
test('nextLesson returns the following lesson without wrapping', () => {
  const lessons = [{ id: 'one' }, { id: 'two' }];
  assert.deepStrictEqual(nextLesson(lessons, 'one'), lessons[1]);
  assert.strictEqual(nextLesson(lessons, 'two'), null);
});
