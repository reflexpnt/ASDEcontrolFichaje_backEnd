self.addEventListener('install', function(e) {
  console.log('Service Worker instalado');
  self.skipWaiting();
});

self.addEventListener('fetch', function(event) {
  // No manejamos caché, solo registramos
});