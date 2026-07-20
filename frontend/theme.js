(function (global) {
  'use strict';

  const THEME_KEY = 'theme';
  const DARK_THEME_COLOR = '#221A14';
  const LIGHT_THEME_COLOR = '#F7F0E6';

  function resolveInitialTheme(stored, osPrefersDark) {
    if (stored === 'dark' || stored === 'light') return stored;
    return osPrefersDark ? 'dark' : 'light';
  }

  function updateThemeUI() {
    if (typeof document === 'undefined') return;

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const themeColor = document.querySelector('meta[name="theme-color"]');
    themeColor?.setAttribute('content', isDark ? DARK_THEME_COLOR : LIGHT_THEME_COLOR);

    ['btnLight', 'heroLight'].forEach((id) => {
      const button = document.getElementById(id);
      button?.classList.toggle('active', !isDark);
      button?.setAttribute('aria-pressed', String(!isDark));
    });
    ['btnDark', 'heroDark'].forEach((id) => {
      const button = document.getElementById(id);
      button?.classList.toggle('active', isDark);
      button?.setAttribute('aria-pressed', String(isDark));
    });

    const mobileButton = document.getElementById('mobileThemeBtn');
    if (mobileButton) {
      const nextTheme = isDark ? 'light' : 'dark';
      mobileButton.textContent = isDark ? '☀' : '🌙';
      mobileButton.setAttribute('aria-label', `Switch to ${nextTheme} theme`);
      mobileButton.setAttribute('title', `Switch to ${nextTheme} theme`);
    }
  }

  function applyTheme(theme) {
    if (typeof document === 'undefined') return;

    const activeTheme = theme === 'dark' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', activeTheme);
    updateThemeUI();
  }

  function setTheme(theme) {
    if (theme !== 'dark' && theme !== 'light') return;

    try {
      global.localStorage?.setItem(THEME_KEY, theme);
    } catch (_) {
      // Theme switching still works when browser storage is unavailable.
    }
    applyTheme(theme);
  }

  function toggleTheme() {
    if (typeof document === 'undefined') return;
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    setTheme(isDark ? 'light' : 'dark');
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { resolveInitialTheme, THEME_KEY };
  }

  if (!global || typeof global.document === 'undefined') return;

  global.applyTheme = applyTheme;
  global.setTheme = setTheme;
  global.toggleTheme = toggleTheme;
  global.updateThemeUI = updateThemeUI;

  let storedTheme = null;
  try {
    storedTheme = global.localStorage?.getItem(THEME_KEY) ?? null;
  } catch (_) {
    // Fall back to the OS preference when browser storage is unavailable.
  }
  const osPrefersDark = global.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false;
  applyTheme(resolveInitialTheme(storedTheme, osPrefersDark));

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateThemeUI, { once: true });
  }
})(typeof window !== 'undefined' ? window : globalThis);
