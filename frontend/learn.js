/* ============================================================
   Luganda AI Studio — beginner path player
   Lesson content is never authored here. Every step names a ref
   into the curated datasets and the text is fetched at runtime,
   so a lesson can never drift from the curated source.
   ============================================================ */

// ── Pure logic (unit tested in tests/learn.test.js) ───────────

// Returns the next step index, or null when the lesson is finished.
function nextStep(index, total) {
  const next = index + 1;
  return next < total ? next : null;
}

// Turns a list of per-step booleans into a session summary.
function scoreSession(results) {
  const correct = results.filter(Boolean).length;
  return { seen: results.length, correct, wrong: results.length - correct };
}

// Answer plus up to three distractors drawn from the same lesson,
// shuffled deterministically so tests can pin the order.
function buildChoices(answer, pool, rand = Math.random) {
  const distractors = [];
  for (const candidate of pool) {
    if (candidate !== answer && !distractors.includes(candidate)) distractors.push(candidate);
  }
  // Deterministic shuffle: caller supplies rand for testability.
  for (let i = distractors.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [distractors[i], distractors[j]] = [distractors[j], distractors[i]];
  }
  const choices = [answer, ...distractors.slice(0, 3)];
  for (let i = choices.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [choices[i], choices[j]] = [choices[j], choices[i]];
  }
  return choices;
}

// ── Browser-only glue ─────────────────────────────────────────
if (typeof document !== 'undefined') {
  const SETUP_KEYS = { goal: 'pilot.goal', focus: 'pilot.focus', minutes: 'pilot.minutes' };
  const LESSON_STATE_KEY = 'pilot.lessons';

  const state = { lessons: [], phrases: new Map(), vocab: new Map(), current: null };

  function readLessonState() {
    try { return JSON.parse(localStorage.getItem(LESSON_STATE_KEY)) || {}; } catch { return {}; }
  }
  function writeLessonState(map) {
    try { localStorage.setItem(LESSON_STATE_KEY, JSON.stringify(map)); } catch { /* storage full or blocked */ }
  }
  function hasSetup() {
    return Object.values(SETUP_KEYS).some(k => localStorage.getItem(k));
  }

  // Resolve a step ref to its curated entry. Returns null if missing,
  // so a bad ref shows an honest message instead of invented text.
  function resolveStep(step) {
    if (step.ref_type === 'sentence') return state.phrases.get(step.ref) || null;
    if (step.ref_type === 'vocabulary') return state.vocab.get(step.ref) || null;
    return null;
  }

  function show(id) {
    ['setup', 'path', 'player', 'summary'].forEach(section => {
      const el = document.getElementById(section);
      if (el) el.hidden = section !== id;
    });
  }

  // ── Setup card ──────────────────────────────────────────────
  function initSetup() {
    document.querySelectorAll('.setup-option').forEach(button => {
      button.addEventListener('click', () => {
        const group = button.dataset.group;
        document.querySelectorAll(`.setup-option[data-group="${group}"]`)
          .forEach(b => b.classList.toggle('selected', b === button));
      });
    });
    const save = document.getElementById('setup-save');
    if (save) save.addEventListener('click', () => {
      Object.entries(SETUP_KEYS).forEach(([group, key]) => {
        const chosen = document.querySelector(`.setup-option[data-group="${group}"].selected`);
        if (chosen) localStorage.setItem(key, chosen.dataset.value);
      });
      if (typeof sendEvent === 'function') sendEvent('onboarding_completed');
      renderPath();
      show('path');
    });
    document.querySelectorAll('.setup-skip').forEach(link =>
      link.addEventListener('click', event => { event.preventDefault(); renderPath(); show('path'); }));
  }

  // ── Lesson list ─────────────────────────────────────────────
  function renderPath() {
    const list = document.getElementById('lesson-list');
    if (!list) return;
    const done = readLessonState();
    list.replaceChildren();
    state.lessons.forEach(lesson => {
      const record = done[lesson.id];
      const card = document.createElement('button');
      card.type = 'button';
      card.className = 'lesson-card' + (record && record.completed ? ' done' : '');
      const title = document.createElement('span');
      title.className = 'lesson-title';
      title.textContent = lesson.title;
      const meta = document.createElement('span');
      meta.className = 'lesson-meta';
      meta.textContent = record && record.completed
        ? `Done. ${record.correct} of ${record.correct + record.wrong} right.`
        : `${lesson.steps.length} steps`;
      card.append(title, meta);
      card.addEventListener('click', () => startLesson(lesson));
      list.append(card);
    });
  }

  // ── Player ──────────────────────────────────────────────────
  function startLesson(lesson) {
    state.current = { lesson, index: 0, results: [] };
    if (typeof sendEvent === 'function') sendEvent('lesson_started', lesson.id);
    show('player');
    renderStep();
  }

  function renderStep() {
    const { lesson, index } = state.current;
    const step = lesson.steps[index];
    const entry = resolveStep(step);
    const stage = document.getElementById('player-stage');
    const progress = document.getElementById('player-progress');
    const bar = document.getElementById('player-bar');
    if (progress) progress.textContent = `Step ${index + 1} of ${lesson.steps.length}`;
    if (bar) bar.style.width = `${Math.round((index / lesson.steps.length) * 100)}%`;
    stage.replaceChildren();

    if (!entry) {
      const miss = document.createElement('p');
      miss.className = 'player-error';
      miss.textContent = 'This step is unavailable. Check the app is running, then try again.';
      stage.append(miss);
      stage.append(continueButton('Skip this step', () => advance(false)));
      return;
    }

    const luganda = document.createElement('p');
    luganda.className = 'step-luganda';
    luganda.textContent = entry.luganda;
    stage.append(luganda);

    if (step.mode === 'show') {
      const english = document.createElement('p');
      english.className = 'step-english';
      english.textContent = entry.english;
      stage.append(english);
      const note = entry.notes || entry.example_english;
      if (note) {
        const hint = document.createElement('p');
        hint.className = 'step-note';
        hint.textContent = note;
        stage.append(hint);
      }
      stage.append(continueButton('Continue', () => advance(true)));
      return;
    }

    // choice: pick the English meaning, distractors from this lesson only
    const prompt = document.createElement('p');
    prompt.className = 'step-prompt';
    prompt.textContent = 'What does this mean?';
    stage.append(prompt);

    const pool = lesson.steps.map(resolveStep).filter(Boolean).map(e => e.english);
    const choices = buildChoices(entry.english, pool);
    const group = document.createElement('div');
    group.className = 'choice-group';
    choices.forEach(choice => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'choice';
      button.textContent = choice;
      button.addEventListener('click', () => revealAnswer(group, button, choice === entry.english, entry));
      group.append(button);
    });
    stage.append(group);
  }

  // Wrong answer shows the right one and moves on: no retry, no requeue.
  function revealAnswer(group, picked, isCorrect, entry) {
    group.querySelectorAll('.choice').forEach(button => {
      button.disabled = true;
      if (button.textContent === entry.english) button.classList.add('right');
    });
    if (!isCorrect) picked.classList.add('wrong');
    const verdict = document.createElement('p');
    verdict.className = 'step-verdict';
    verdict.textContent = isCorrect ? 'Correct.' : `Not quite. It means "${entry.english}".`;
    const stage = document.getElementById('player-stage');
    stage.append(verdict);
    const note = entry.notes || entry.example_english;
    if (note) {
      const hint = document.createElement('p');
      hint.className = 'step-note';
      hint.textContent = note;
      stage.append(hint);
    }
    stage.append(continueButton('Continue', () => advance(isCorrect)));
  }

  function continueButton(label, onClick) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'btn-primary step-continue';
    button.textContent = label;
    button.addEventListener('click', onClick);
    return button;
  }

  function advance(wasCorrect) {
    state.current.results.push(wasCorrect);
    const next = nextStep(state.current.index, state.current.lesson.steps.length);
    if (next === null) return finishLesson();
    state.current.index = next;
    renderStep();
  }

  async function finishLesson() {
    const { lesson, results } = state.current;
    const score = scoreSession(results);

    const done = readLessonState();
    done[lesson.id] = { completed: true, correct: score.correct, wrong: score.wrong };
    writeLessonState(done);
    if (typeof sendEvent === 'function') sendEvent('lesson_completed', lesson.id);

    const line = document.getElementById('summary-score');
    if (line) line.textContent = `${score.correct} of ${score.seen} right.`;
    if (typeof recordSessionComplete === 'function') recordSessionComplete();
    if (typeof setMascot === 'function') setMascot('summary-mascot', 'kintu', 'celebrate');

    show('summary');
    renderPath();

    try {
      await fetch('/api/v1/teach/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cards_seen: score.seen,
          correct: score.correct,
          wrong: score.wrong,
          session_date: new Date().toISOString().slice(0, 10),
        }),
      });
    } catch { /* offline: local state already saved */ }
  }

  // ── Boot ────────────────────────────────────────────────────
  async function init() {
    initSetup();
    const back = document.getElementById('summary-back');
    if (back) back.addEventListener('click', () => show('path'));

    try {
      const [lessonsRes, phrasesRes, vocabRes] = await Promise.all([
        fetch('/api/v1/library/lessons'),
        fetch('/api/v1/library/phrases'),
        fetch('/api/v1/library/vocabulary'),
      ]);
      if (!lessonsRes.ok || !phrasesRes.ok || !vocabRes.ok) throw new Error('library unavailable');
      const lessonsData = await lessonsRes.json();
      const phrasesData = await phrasesRes.json();
      const vocabData = await vocabRes.json();

      state.lessons = lessonsData.lessons || [];
      (phrasesData.entries || []).forEach(e => state.phrases.set(e.id, e));
      (vocabData.entries || []).forEach(e => state.vocab.set(e.key, e));
    } catch {
      const list = document.getElementById('lesson-list');
      if (list) {
        const error = document.createElement('p');
        error.className = 'player-error';
        error.textContent = 'Cannot load lessons. Check the app is running, then try again.';
        list.replaceChildren(error);
      }
      show('path');
      return;
    }

    renderPath();
    const startAt = hasSetup() ? 'path' : 'setup';
    if (startAt === 'setup' && typeof sendEvent === 'function') sendEvent('onboarding_started');
    show(startAt);
  }

  document.addEventListener('DOMContentLoaded', init);
}

// Node-testability — no effect in the browser, where `module` is undefined.
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { nextStep, scoreSession, buildChoices };
}