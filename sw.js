const CACHE = 'cuhk-bus-v1';
const FILES = [
    '/', '/index.html', '/stop.json', '/route.json',
    '/route_segment.json', '/manifest.json', '/icon.svg'
];

self.addEventListener('install', e => {
    e.waitUntil((async () => {
        const c = await caches.open(CACHE);
        await c.addAll(FILES);
        await self.skipWaiting();
    })());
});

self.addEventListener('activate', e => {
    e.waitUntil((async () => {
        for (const key of await caches.keys()) {
            if (key !== CACHE) await caches.delete(key);
        }
        await self.clients.claim();
    })());
});

self.addEventListener('fetch', e => {
    e.respondWith((async () => {
        const r = await caches.match(e.request);
        if (r) return r;
        try {
            const res = await fetch(e.request);
            const c = await caches.open(CACHE);
            c.put(e.request, res.clone());
            return res;
        } catch {
            return new Response('', { status: 503 });
        }
    })());
});
