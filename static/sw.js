const CACHE_NAME = 'moodify-aura-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/songs.json',
  '/static/logo-192.png',
  '/static/logo-512.png',
  '/static/favicon.png',
  'https://cdn.tailwindcss.com',
  'https://cdn.jsdelivr.net/npm/@vladmandic/face-api/dist/face-api.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Outfit:wght@400;600;800;900&display=swap'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      // Ignore failures on optional external resources during install
      return Promise.allSettled(
        ASSETS_TO_CACHE.map(asset => {
          return cache.add(asset).catch(err => {
            console.warn(`Failed to pre-cache asset: ${asset}`, err);
          });
        })
      );
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  // Let API requests bypass the service worker (network-only)
  if (event.request.url.includes('/api/') || event.request.url.includes('/recommend/')) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        // Fetch fresh copy in background to update cache for next time
        fetch(event.request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, networkResponse));
          }
        }).catch(() => {});
        return cachedResponse;
      }
      return fetch(event.request).then((response) => {
        if (!response || response.status !== 200 || response.type !== 'basic') {
          return response;
        }
        const responseToCache = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return response;
      });
    })
  );
});
