import { test, expect } from '@playwright/test';

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL ?? 'admin@civic-education.ss';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD ?? 'AdminPass123!';

test.describe('Live API login', () => {
  test('user can log in against the real backend', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(ADMIN_EMAIL);
    await page.getByLabel(/password/i).fill(ADMIN_PASSWORD);
    await page.getByRole('button', { name: /log in/i }).click();

    await expect(page).not.toHaveURL(/\/login/, { timeout: 15_000 });
    await expect(page.getByText(/platform demo|articles|quizzes/i).first()).toBeVisible({
      timeout: 15_000,
    });
  });
});

test.describe('Live API health', () => {
  test('backend readiness endpoint responds', async ({ request }) => {
    const apiBase = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000';
    const response = await request.get(`${apiBase}/api/ready/`);
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.status).toBe('ready');
  });
});
