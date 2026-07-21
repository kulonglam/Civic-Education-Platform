import { test, expect } from '@playwright/test';
import { apiGlob, mockSession } from './helpers';

test.describe('Billing page', () => {
  test.beforeEach(async ({ page }) => {
    await mockSession(
      page,
      {
        email: 'admin@test.com',
        first_name: 'Admin',
        last_name: 'User',
        role: { id: 1, name: 'admin' },
      },
      { memberRole: 'owner' }
    );
  });

  test('displays subscription and plan options', async ({ page }) => {
    await page.route(apiGlob('billing/plans/**'), async (route) => {
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

    await page.route(apiGlob('billing/subscription/**'), async (route) => {
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
