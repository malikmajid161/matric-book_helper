const CACHE = 'ptb-scholar-shell-v1';
self.addEventListener('install', event => {event.waitUntil(caches.open(CACHE).then(cache => cache.add('/'))); self.skipWaiting();});
self.addEventListener('activate', event => {event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith('ptb-scholar-shell-') && key !== CACHE).map(key => caches.delete(key))))); self.clients.claim();});
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== self.location.origin || (!url.pathname.startsWith('/_next/static/') && event.request.mode !== 'navigate')) return;
  event.respondWith(fetch(event.request).then(response => {
    if (response.ok) {const copy = response.clone(); event.waitUntil(caches.open(CACHE).then(cache => cache.put(event.request, copy)));}
    return response;
  }).catch(async () => {const cache = await caches.open(CACHE); return await cache.match(event.request) || (event.request.mode === 'navigate' ? await cache.match('/') : undefined) || Response.error();}));
});
