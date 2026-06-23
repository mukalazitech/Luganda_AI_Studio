// frontend/streak.js
// Shared daily-streak + session-XP logic for Luganda AI Studio.
// Streak persists across days via localStorage; XP is in-memory per session.

const STREAK_KEY = 'luganda_streak_v1';

function _todayStr() {
  return new Date().toISOString().slice(0, 10); // 'YYYY-MM-DD'
}

function _yesterdayStr() {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  return d.toISOString().slice(0, 10);
}

function getStreak() {
  try {
    const raw = localStorage.getItem(STREAK_KEY);
    if (!raw) return { count: 0, lastDate: null };
    const parsed = JSON.parse(raw);
    if (typeof parsed.count !== 'number' || typeof parsed.lastDate !== 'string') {
      return { count: 0, lastDate: null };
    }
    return parsed;
  } catch (e) {
    return { count: 0, lastDate: null };
  }
}

// Call once when a Teach session completes (flash or quiz "Session Complete!" screen).
// Returns the updated streak object. Increments at most once per calendar day;
// resets to 1 if the last completed day was before yesterday (streak broken).
function recordSessionComplete() {
  const today = _todayStr();
  const streak = getStreak();

  if (streak.lastDate === today) {
    // Already recorded today — no change.
    return streak;
  }

  const yesterday = _yesterdayStr();
  const newCount = (streak.lastDate === yesterday) ? streak.count + 1 : 1;
  const updated = { count: newCount, lastDate: today };
  localStorage.setItem(STREAK_KEY, JSON.stringify(updated));
  return updated;
}

// Renders the streak count into any element with id="streakPill" on the current page.
// Safe to call on pages that don't have the element (no-op).
function renderStreakPill() {
  const el = document.getElementById('streakPill');
  if (!el) return;
  const streak = getStreak();
  el.textContent = streak.count > 0 ? `🔥 ${streak.count}` : '🔥 0';
  el.title = streak.count > 0
    ? `${streak.count} day streak — keep it up!`
    : 'Complete a Teach session to start your streak';
}

document.addEventListener('DOMContentLoaded', renderStreakPill);
