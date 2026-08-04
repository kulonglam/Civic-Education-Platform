// Background Sync: relay to the main thread which holds the IndexedDB logic
self.addEventListener('sync', (event) => {
  if (event.tag === 'cep-write-queue') {
    event.waitUntil(
      self.clients.matchAll({ includeUncontrolled: true, type: 'window' }).then((clients) => {
        clients.forEach((client) => client.postMessage({ type: 'cep:bg-sync' }));
      }),
    );
  }
});

self.addEventListener('push', (event) => {
  let data = { title: 'Civic Education RSS', body: '' };
  try {
    data = event.data ? event.data.json() : data;
  } catch {
    data.body = event.data ? event.data.text() : '';
  }
  event.waitUntil(
    self.registration.showNotification(data.title || 'Civic Education RSS', {
      body: data.body || '',
      icon: '/icon-192.png',
    }),
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(clients.openWindow('/notifications'));
});
