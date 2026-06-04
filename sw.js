const CACHE = 'cuhk-bus-v2';
const CORE = [
    './',
    './index.html',
    './stop.json',
    './route.json',
    './route_segment.json',
    './manifest.json',
    './icon.svg',
    './icons/icon-192.png',
    './icons/icon-512.png'
];
const VENDOR = [
    './vendor/tw.css',
    './vendor/leaflet/leaflet.css',
    './vendor/leaflet/leaflet.js',
    './vendor/leaflet/images/marker-icon.png',
    './vendor/leaflet/images/marker-icon-2x.png',
    './vendor/leaflet/images/marker-shadow.png',
    './vendor/placeholder-tile.png'
];
const PRECACHE = [...CORE, ...VENDOR];

const RUNTIME_CACHE = 'cuhk-bus-runtime-v2';
const STALE_REVALIDATE_HOSTS = [
    'cdn.tailwindcss.com',
    'unpkg.com',
    'fonts.googleapis.com',
    'fonts.gstatic.com'
];

self.addEventListener('install', e => {
    e.waitUntil((async () => {
        const c = await caches.open(CACHE);
        await c.addAll(PRECACHE);
        await self.skipWaiting();
    })());
});

self.addEventListener('activate', e => {
    e.waitUntil((async () => {
        for (const key of await caches.keys()) {
            if (key !== CACHE && key !== RUNTIME_CACHE) await caches.delete(key);
        }
        await self.clients.claim();
    })());
});

self.addEventListener('fetch', e => {
    const req = e.request;
    if (req.method !== 'GET') return;

    const url = new URL(req.url);

    if (req.mode === 'navigate') {
        e.respondWith((async () => {
            try {
                const fresh = await fetch(req);
                const c = await caches.open(CACHE);
                c.put('./index.html', fresh.clone());
                return fresh;
            } catch {
                const cached = await caches.match('./index.html');
                if (cached) return cached;
                return new Response('Offline', { status: 503 });
            }
        })());
        return;
    }

    if (STALE_REVALIDATE_HOSTS.includes(url.hostname)) {
        e.respondWith((async () => {
            const c = await caches.open(RUNTIME_CACHE);
            const cached = await c.match(req);
            const fetchPromise = fetch(req).then(res => {
                if (res && (res.ok || res.type === 'opaque')) {
                    c.put(req, res.clone());
                }
                return res;
            }).catch(() => null);
            return cached || (await fetchPromise) || new Response('', { status: 503 });
        })());
        return;
    }

    if (url.hostname.endsWith('tile.openstreetmap.org')) {
        e.respondWith((async () => {
            try {
                const res = await fetch(req);
                const c = await caches.open(RUNTIME_CACHE);
                c.put(req, res.clone());
                return res;
            } catch {
                const placeholder = await caches.match('./vendor/placeholder-tile.png');
                if (placeholder) return placeholder;
                return new Response('', { status: 503 });
            }
        })());
        return;
    }

    if (url.origin === self.location.origin) {
        e.respondWith((async () => {
            const cached = await caches.match(req);
            if (cached) return cached;
            try {
                const res = await fetch(req);
                const c = await caches.open(CACHE);
                c.put(req, res.clone());
                return res;
            } catch {
                return new Response('', { status: 503 });
            }
        })());
        return;
    }
});
