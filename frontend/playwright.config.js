import { defineConfig, devices } from '@playwright/test';

const isLive = process.env.E2E_LIVE === '1';
const apiBase = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000';
const webBase = process.env.E2E_WEB_URL ?? 'http://127.0.0.1:5173';

const webServers = isLive
  ? [
      {
        command:
          process.platform === 'win32'
            ? 'cd ..\\backend && ..\\backend\\venv\\Scripts\\python.exe manage.py runserver 127.0.0.1:8000'
            : 'cd ../backend && python manage.py runserver 127.0.0.1:8000',
        url: `${apiBase}/api/health/`,
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
        env: {
          DJANGO_SETTINGS_MODULE: 'config.settings.development',
          ...process.env,
        },
      },
      {
        command: 'npm run dev -- --host 127.0.0.1 --port 5173',
        url: webBase,
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
      },
    ]
  : [
      {
        command: 'npm run dev -- --host 127.0.0.1 --port 5173',
        url: webBase,
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
      },
    ];

export default defineConfig({
  testDir: './e2e',
  testMatch: isLive ? 'live/**/*.spec.js' : '*.spec.js',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'list',
  use: {
    baseURL: webBase,
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: webServers,
});
