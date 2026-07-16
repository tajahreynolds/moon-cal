{% load static %}// Daily Signal service worker — offline-capable PWA shell.
const CACHE = "signal-v1";
const PRECACHE = [
  "{% static 'horoscope/app.css' %}",
  "{% static 'horoscope/js/ticker.js' %}",
  "{% static 'horoscope/js/drawer.js' %}",
  "{% static 'horoscope/js/sw-register.js' %}",
  "{% static 'horoscope/icons/icon-192.png' %}",
  "{% url 'horoscope:offline' %}"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // Cache-first for static assets.
  if (url.pathname.startsWith("/static/")) {
    event.respondWith(
      caches.match(req).then((hit) => hit || fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
        return res;
      }))
    );
    return;
  }

  // Network-first for navigations, falling back to cache then the offline page.
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
        return res;
      }).catch(() =>
        caches.match(req).then((hit) => hit || caches.match("{% url 'horoscope:offline' %}"))
      )
    );
  }
});
