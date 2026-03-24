const CACHE = 'hv-v19';
const FILES = [
  './',
  './index.html',
  './manifest.json',
  './obslosa.html',
  './fors.html',
  './pedars.html',
  './postschema.html',
  './eobusare.html',
  './obo.html',
  './rassoika.html',
  './what.html',
  './scrim.html',
  './weft.html',
  './ah.html'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});
