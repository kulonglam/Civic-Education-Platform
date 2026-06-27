import { test, expect } from '@playwright/test';

const API = process.env.E2E_API_URL
  ? `${process.env.E2E_API_URL}/api`
  : 'http://127.0.0.1:8000/api';

test.describe('Live forum', () => {
  test('shows seeded approved topic', async ({ page, request }) => {
    const login = await request.post(`${API}/auth/login/`, {
      data: { email: 'admin@civic-education.ss', password: 'AdminPass123!' },
    });
    expect(login.ok()).toBeTruthy();
    const tokens = await login.json();

    await page.addInitScript(({ access, slug }) => {
      localStorage.setItem('cep_access', access);
      localStorage.setItem('cep_refresh', 'refresh-not-needed-for-read');
      localStorage.setItem('cep_org_slug', slug);
    }, { access: tokens.access, slug: 'platform-demo' });

    await page.goto('/forum');
    await expect(page.getByRole('heading', { name: /forum|community/i })).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText(/youth participate in local governance/i)).toBeVisible({ timeout: 15_000 });
  });
});
