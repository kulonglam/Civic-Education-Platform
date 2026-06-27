import { test, expect } from '@playwright/test';

const API = 'http://127.0.0.1:8000/api';

test.describe('Login flow', () => {
  test('user can log in with valid credentials', async ({ page }) => {
    await page.route(`${API}/auth/login/`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access: 'fake-access-token',
          refresh: 'fake-refresh-token',
        }),
      });
    });

    await page.route(`${API}/users/profile/`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: '1',
          email: 'user@test.com',
          first_name: 'Test',
          last_name: 'User',
          role: { id: 1, name: 'citizen' },
          is_active: true,
          email_verified: true,
          created_at: '2026-01-01',
          profile: { bio: '', avatar_url: '', preferred_language: 'en' },
        }),
      });
    });

    await page.goto('/login');
    await page.getByLabel(/email/i).fill('user@test.com');
    await page.getByLabel(/password/i).fill('TestPass123!');
    await page.getByRole('button', { name: /log in/i }).click();

    await expect(page).not.toHaveURL(/\/login/);
  });

  test('shows error for invalid credentials', async ({ page }) => {
    await page.route(`${API}/auth/login/`, async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid credentials.' }),
      });
    });

    await page.goto('/login');
    await page.getByLabel(/email/i).fill('bad@test.com');
    await page.getByLabel(/password/i).fill('wrong');
    await page.getByRole('button', { name: /log in/i }).click();

    await expect(page.getByText(/invalid credentials/i)).toBeVisible();
  });
});
