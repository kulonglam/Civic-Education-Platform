import { test, expect } from '@playwright/test';

const API = 'http://127.0.0.1:8000/api';

test.describe('Billing page', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('cep_access', 'fake-token');
      localStorage.setItem('cep_refresh', 'fake-refresh');
      localStorage.setItem('cep_org_slug', 'platform-demo');
    });

    await page.route(`${API}/users/profile/`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: '1',
          email: 'admin@test.com',
          first_name: 'Admin',
          last_name: 'User',
          role: { id: 1, name: 'admin' },
          is_active: true,
          email_verified: true,
          created_at: '2026-01-01',
          profile: { bio: '', avatar_url: '', preferred_language: 'en' },
        }),
      });
    });

    await page.route(`${API}/organization/current/`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'org-1',
          name: 'Platform Demo',
          slug: 'platform-demo',
          tagline: '',
          logo_url: '',
          primary_color: '#059669',
          is_active: true,
          created_at: '2026-01-01',
        }),
      });
    });

    await page.route(`${API}/organization/members/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          count: 1,
          results: [
            {
              id: 'm1',
              user: '1',
              user_email: 'admin@test.com',
              user_name: 'Admin User',
              role: 'owner',
              created_at: '2026-01-01',
            },
          ],
        }),
      });
    });

    await page.route(`${API}/organization/mine/`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 'm1',
            role: 'owner',
            organization: {
              id: 'org-1',
              name: 'Platform Demo',
              slug: 'platform-demo',
              tagline: '',
              logo_url: '',
              primary_color: '#059669',
              is_active: true,
              created_at: '2026-01-01',
            },
            created_at: '2026-01-01',
          },
        ]),
      });
    });
  });

  test('displays subscription and plan options', async ({ page }) => {
    await page.route(`${API}/billing/plans/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          count: 2,
          results: [
            {
              id: 'p1',
              code: 'free',
              name: 'Free',
              price_cents: 0,
              currency: 'USD',
              interval: 'month',
              max_members: 5,
              max_articles: 10,
              max_quizzes: 5,
              features: {},
            },
            {
              id: 'p2',
              code: 'pro',
              name: 'Pro',
              price_cents: 2900,
              currency: 'USD',
              interval: 'month',
              max_members: 50,
              max_articles: 500,
              max_quizzes: 50,
              features: {},
            },
          ],
        }),
      });
    });

    await page.route(`${API}/billing/subscription/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          subscription: {
            id: 's1',
            plan: {
              id: 'p1',
              code: 'free',
              name: 'Free',
              price_cents: 0,
              currency: 'USD',
              interval: 'month',
              max_members: 5,
              max_articles: 10,
              max_quizzes: 5,
              features: {},
            },
            status: 'active',
            current_period_end: null,
            cancel_at_period_end: false,
            created_at: '2026-01-01',
          },
          usage: {
            members: { used: 2, limit: 5 },
            articles: { used: 3, limit: 10 },
            quizzes: { used: 1, limit: 5 },
          },
        }),
      });
    });

    await page.goto('/billing');
    await expect(page.getByRole('heading', { name: /billing & plans/i })).toBeVisible();
    await expect(page.getByText('Free').first()).toBeVisible();
    await expect(page.getByText('Pro')).toBeVisible();
    await expect(page.getByRole('button', { name: /upgrade/i })).toBeVisible();
  });
});
