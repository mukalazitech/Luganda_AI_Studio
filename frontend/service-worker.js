/* ============================================================
   Luganda AI Studio — Service Worker
   Strategy: Network-first for HTML documents (falls back to cache
             offline, so learners always see the latest page).
             Cache-first for static assets (JS, CSS, icons, fonts).
             Network-first for API calls (never cache these).
   ============================================================ */

const CACHE_NAME = 'luganda-studio-v2';

// UI shell assets to cache on install
const PRECACHE_ASSETS = [
  '/app/index.html',
  '/app/translate.html',
  '/app/search.html',
  '/app/teach.html',
  '/app/chat.html',
  '/app/reviews.html',
  '/app/explore.html',
  '/app/proverbs.html',
  '/app/grammar.html',
  '/app/phrases.html',
  '/app/library.html',
  '/app/theme.js',
  '/app/manifest.json',
  '/app/icons/icon-192.svg',
  '/app/icons/icon-512.svg',
  '/app/assets/icons.svg',
];

// ── Install — pre-cache the UI shell ──────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(PRECACHE_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

// ── Activate — clean up old caches ────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

// ── Fetch — route requests ─────────────────────────────────────
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Never intercept API calls — always go to the network
  if (url.pathname.startsWith('/api/')) {
    return; // fall through to network
  }

  // Never intercept non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Network-first for HTML documents — always show the latest page;
  // fall back to cache only when the network is unavailable.
  if (event.request.mode === 'navigate' || event.request.destination === 'document') {
    event.respondWith(
      fetch(event.request).then(response => {
        if (response && response.status === 200 && response.type === 'basic') {
          const toCache = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, toCache);
          });
        }
        return response;
      }).catch(() => {
        return caches.match(event.request).then(cached => cached || caches.match('/app/index.html'));
      })
    );
    return;
  }

  // Cache-first for everything else (CSS, JS, fonts, icons)
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) {
        return cached;
      }

      // Not in cache — fetch from network and cache the result
      return fetch(event.request).then(response => {
        // Only cache successful same-origin responses
        if (
          !response ||
          response.status !== 200 ||
          response.type !== 'basic'
        ) {
          return response;
        }

        const toCache = response.clone();
        caches.open(CACHE_NAME).then(cache => {
          cache.put(event.request, toCache);
        });

        return response;
      }).catch(() => {
        // Network failed and not in cache — nothing more we can do
        return undefined;
      });
    })
  );
});
