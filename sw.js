const STATIC_CACHE = 'k1980-static-v1';
const API_CACHE = 'k1980-api-v1';

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then(cache => cache.addAll(['/', '/index.html', '/manifest.json']))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== STATIC_CACHE && k !== API_CACHE).map(k => caches.delete(k))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (url.hostname.includes('supabase.co')) {
    event.respondWith(
      fetch(event.request).then(r => {
        if (r.ok) caches.open(API_CACHE).then(c => c.put(event.request, r.clone()));
        return r;
      }).catch(() => caches.match(event.request))
    );
    return;
  }
  event.respondWith(
    caches.match(event.request).then(cached => cached || fetch(event.request))
  );
});

self.addEventListener('push', event => {
  if (!event.data) return;
  const d = event.data.json();
  event.waitUntil(
    self.registration.showNotification(d.title || 'K1980', {
      body: d.body || '', icon: '/icons/icon-192.png', data: { url: d.url || '/' }
    })
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  clients.openWindow(event.notification.data.url);
});
