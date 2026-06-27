import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const apiBase = env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';
  const apiOrigin = apiBase.replace(/\/api\/?$/, '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  return {
    plugins: [
      react(),
      VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['civic-education-logo.png', 'icon-192.png', 'icon-512.png'],
        manifest: {
          name: 'Civic Education Platform',
          short_name: 'CivicEd',
          description: 'Civic education for citizens of South Sudan',
          theme_color: '#059669',
          background_color: '#ffffff',
          display: 'standalone',
          orientation: 'portrait',
          start_url: '/',
          lang: 'en',
          icons: [
            {
              src: '/icon-192.png',
              sizes: '192x192',
              type: 'image/png',
              purpose: 'any',
            },
            {
              src: '/icon-512.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'any',
            },
            {
              src: '/icon-512.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'maskable',
            },
          ],
        },
        workbox: {
          importScripts: ['push-sw.js'],
          globPatterns: ['**/*.{js,css,html,ico,svg,woff2}'],
          navigateFallback: '/index.html',
          navigateFallbackDenylist: [/^\/api/],
          runtimeCaching: [
            {
              urlPattern: new RegExp(`^${apiOrigin}/api/articles`, 'i'),
              handler: 'StaleWhileRevalidate',
              options: {
                cacheName: 'cep-api-articles',
                expiration: { maxEntries: 80, maxAgeSeconds: 60 * 60 * 24 },
                cacheableResponse: { statuses: [0, 200] },
              },
            },
            {
              urlPattern: new RegExp(`^${apiOrigin}/api/categories`, 'i'),
              handler: 'StaleWhileRevalidate',
              options: {
                cacheName: 'cep-api-categories',
                expiration: { maxEntries: 20, maxAgeSeconds: 60 * 60 * 24 },
                cacheableResponse: { statuses: [0, 200] },
              },
            },
            {
              urlPattern: ({ request }) => request.destination === 'image',
              handler: 'CacheFirst',
              options: {
                cacheName: 'cep-media',
                expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 30 },
                cacheableResponse: { statuses: [0, 200] },
              },
            },
          ],
        },
        devOptions: {
          enabled: false,
        },
      }),
    ],
    test: {
      globals: false,
      environment: 'jsdom',
      setupFiles: ['./src/test/setup.js'],
      css: true,
      include: ['src/**/*.{test,spec}.{js,jsx}'],
    },
  };
});
