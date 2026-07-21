'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { PRIMARY, TOOLS, INTERNAL } = require('../nav-spec.js');

const FRONTEND_DIR = path.resolve(__dirname, '..');
const LEARNER_PAGE_CANDIDATES = [
  'index', 'translate', 'search', 'teach', 'learn',
  'explore', 'proverbs', 'grammar', 'phrases', 'library',
];
const LEARNER_PAGES = LEARNER_PAGE_CANDIDATES.filter((page) =>
  fs.existsSync(path.join(FRONTEND_DIR, `${page}.html`))
);
const REQUIRED_PAGES = [
  'index', 'translate', 'search', 'teach',
  'explore', 'proverbs', 'grammar', 'phrases', 'library',
];
const EXPLORE_PAGES = ['explore', 'proverbs', 'grammar', 'phrases', 'library'];

function readPage(page) {
  return fs.readFileSync(path.join(FRONTEND_DIR, `${page}.html`), 'utf8');
}

function classBlock(html, tag, className) {
  const pattern = new RegExp(
    `<${tag}\\b[^>]*class=["'][^"']*\\b${className}\\b[^"']*["'][^>]*>([\\s\\S]*?)<\\/${tag}>`,
    'i',
  );
  const match = html.match(pattern);
  assert.ok(match, `missing <${tag}>.${className}`);
  return match[1];
}

function attribute(source, name) {
  const match = source.match(new RegExp(`\\b${name}=["']([^"']+)["']`, 'i'));
  return match ? match[1] : '';
}

function links(markup) {
  return [...markup.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a>/gi)].map((match) => {
    const body = match[2];
    const iconMatch = body.match(/<use\b[^>]*\bhref=["']\/app\/assets\/icons\.svg#icon-([^"']+)["'][^>]*>/i);
    return {
      href: attribute(match[1], 'href'),
      label: body.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim(),
      icon: iconMatch ? iconMatch[1] : null,
    };
  });
}

function expectedLinks(items) {
  return items.map(({ label, page, icon }) => ({
    href: `${page}.html`,
    label,
    icon,
  }));
}

assert.ok(LEARNER_PAGES.length > 0, 'at least one learner page must exist');

test('all required learner pages exist', () => {
  const missing = REQUIRED_PAGES.filter((page) =>
    !fs.existsSync(path.join(FRONTEND_DIR, `${page}.html`))
  );

  assert.deepStrictEqual(missing, []);
});

test('search accepts a nonblank q query handoff', () => {
  const html = readPage('search');

  assert.match(html, /new URLSearchParams\(location\.search\)\.get\(['"]q['"]\)/);
  assert.match(html, /getElementById\(['"]searchInput['"]\)\.value\s*=\s*\w+/);
  assert.match(html, /if\s*\(\w+\)[\s\S]{0,160}runSearch\(\)/);
});

test('Explore pages use the canonical learner PWA and font head', () => {
  for (const page of EXPLORE_PAGES) {
    const html = readPage(page);
    assert.match(html, /<meta\s+name=["']theme-color["']\s+content=["']#F7F0E6["']\s*\/>/i, `${page}: canonical theme color`);
    assert.match(html, /<meta\s+name=["']apple-mobile-web-app-capable["']\s+content=["']yes["']\s*\/>/i, `${page}: Apple PWA capable`);
    assert.match(html, /<meta\s+name=["']mobile-web-app-capable["']\s+content=["']yes["']\s*\/>/i, `${page}: mobile PWA capable`);
    assert.match(html, /<link\s+rel=["']apple-touch-icon["']\s+href=["']\/app\/icons\/icon-192\.svg["']\s*\/>/i, `${page}: touch icon`);
    assert.match(html, /fonts\.googleapis\.com\/css2\?family=Figtree[^"']+family=DM\+Sans/i, `${page}: canonical learner fonts`);
  }
});

test('phrases ignores and aborts stale TTS requests', () => {
  const html = readPage('phrases');
  assert.match(html, /new AbortController\(\)/);
  assert.match(html, /signal\s*:\s*\w+\.signal/);
  assert.match(html, /requestId\s*!==\s*ttsRequestId/);
});

test('Explore pages use plain, dash-free blocked-state copy', () => {
  const EXPECTED_BLOCKED_COPY = {
    explore: 'Cannot reach the library. Check the app is running, then try again.',
    proverbs: 'Cannot load proverbs. Check the app is running, then try again.',
    grammar: 'Cannot load grammar. Check the app is running, then try again.',
    phrases: 'Cannot load phrases. Check the app is running, then try again.',
    library: 'Cannot load the word library. Check the app is running, then try again.',
  };
  for (const page of EXPLORE_PAGES) {
    const html = readPage(page);
    assert.ok(html.includes(EXPECTED_BLOCKED_COPY[page]), `${page}: new blocked-state copy present`);
    assert.doesNotMatch(html, /is the local server running/i, `${page}: old blocked-state copy removed`);
    // No em dash may appear inside any dynamic user-visible copy string.
    for (const match of html.matchAll(/textContent\s*=\s*(['"])((?:\\.|(?!\1).)*)\1/g)) {
      assert.ok(!match[2].includes('—'), `${page}: em dash in state copy "${match[2]}"`);
    }
  }
});

test('grammar page hides plumbing fields and ships the seven hand-written titles', () => {
  const html = readPage('grammar');
  for (const label of ['Rule Id', 'Tense Id', 'Class Id', 'Needs Review']) {
    assert.ok(!html.includes(label), `grammar: plumbing label leaked into markup: ${label}`);
  }
  for (const field of ['rule_id', 'tense_id', 'class_id', 'needs_review']) {
    assert.match(html, new RegExp(`HIDDEN_FIELDS[\\s\\S]*${field}`), `grammar: ${field} not marked hidden`);
  }
  const HANDWRITTEN_TITLES = [
    'Vowels and their sounds',
    'Consonants and their sounds',
    'The eight word classes',
    'Asking questions',
    'Verb tenses',
    'All tenses at a glance',
    'Who is doing the action',
  ];
  for (const title of HANDWRITTEN_TITLES) {
    assert.ok(html.includes(title), `grammar: missing hand-written title: ${title}`);
  }
});

for (const page of LEARNER_PAGES) {
  test(`${page}: sidebar follows the canonical learner order`, () => {
    const sidebar = classBlock(readPage(page), 'nav', 'sidebar-nav');
    assert.deepStrictEqual(links(sidebar), expectedLinks([...PRIMARY, ...TOOLS]));
  });

  test(`${page}: bottom navigation contains the four primary destinations`, () => {
    const bottom = classBlock(readPage(page), 'nav', 'bottom-nav');
    assert.deepStrictEqual(links(bottom), expectedLinks(PRIMARY));
  });

  test(`${page}: learner navigation excludes internal destinations`, () => {
    const html = readPage(page);
    const shell = [
      classBlock(html, 'nav', 'sidebar-nav'),
      classBlock(html, 'nav', 'bottom-nav'),
    ].join('\n');

    for (const internalPage of INTERNAL) {
      assert.doesNotMatch(shell, new RegExp(`href=["']${internalPage.replace('.', '\\.')}["']`, 'i'));
    }
  });

  test(`${page}: shared theme bootstrap and Home sprite icon are present`, () => {
    const html = readPage(page);
    const sidebar = classBlock(html, 'nav', 'sidebar-nav');
    const bottom = classBlock(html, 'nav', 'bottom-nav');

    assert.match(html, /<script\b[^>]*\bsrc=["']\/app\/theme\.js["'][^>]*><\/script>/i);
    assert.match(sidebar, /<use\b[^>]*\bhref=["']\/app\/assets\/icons\.svg#icon-home["'][^>]*>/i);
    assert.match(bottom, /<use\b[^>]*\bhref=["']\/app\/assets\/icons\.svg#icon-home["'][^>]*>/i);
  });
}
