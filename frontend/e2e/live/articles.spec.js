import { test, expect } from '@playwright/test';

const API = process.env.E2E_API_URL
  ? `${process.env.E2E_API_URL}/api`
  : 'http://127.0.0.1:8000/api';

async function loginAsAdmin(request) {
  const login = await request.post(`${API}/auth/login/`, {
    data: { email: 'admin@civic-education.ss', password: 'AdminPass123!' },
  });
  expect(login.ok()).toBeTruthy();
  return login.json();
}

test.describe('Live articles', () => {
  test('shows seeded articles from real API', async ({ page, request }) => {
    const tokens = await loginAsAdmin(request);

    await page.addInitScript(({ access, slug }) => {
      localStorage.setItem('cep_access', access);
      localStorage.setItem('cep_refresh', 'refresh-not-needed-for-read');
      localStorage.setItem('cep_org_slug', slug);
    }, { access: tokens.access, slug: 'platform-demo' });

    await page.goto('/articles');
    await expect(page.getByRole('heading', { name: /articles/i })).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText(/Transitional Constitution|Local Government|Free and Fair Elections/)).toBeVisible({
      timeout: 15_000,
    });
  });
});
