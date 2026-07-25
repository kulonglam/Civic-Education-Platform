import { test, expect } from '@playwright/test';
import { apiGlob, mockSession } from './helpers';

const TUTOR_DONE = {
  session_id: 'sess-e2e-1',
  reply: 'Civic education helps citizens understand rights, institutions, and participation.',
  sources: [
    {
      article_id: 'art-constitution-1',
      title: 'Understanding the Transitional Constitution',
      source: 'Transitional Constitution of South Sudan, 2011',
      category: 'Constitution',
      category_slug: 'constitution',
      source_kind: 'text+pdf',
      excerpt: 'Fundamental rights and the structure of government…',
    },
  ],
  tokens_used: 42,
  messages_used_today: 1,
  daily_limit: 30,
  messages_remaining: 29,
};

test.describe('AI Tutor (mocked API)', () => {
  test.beforeEach(async ({ page }) => {
    await mockSession(page);

    await page.route(apiGlob('tutor/usage/**'), async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          daily_limit: 30,
          messages_used_today: 0,
          messages_remaining: 30,
          session_message_count: 0,
        }),
      });
    });

    await page.route(apiGlob('tutor/chat/session/**'), async (route) => {
      if (route.request().method() === 'DELETE') {
        await route.fulfill({ status: 204, body: '' });
        return;
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ session_id: '', article_id: null, messages: [] }),
      });
    });

    await page.route(apiGlob('tutor/chat/history/**'), async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await page.route(apiGlob('tutor/chat/**'), async (route) => {
      const url = route.request().url();
      if (url.includes('/session') || url.includes('/history')) {
        await route.fallback();
        return;
      }
      if (url.includes('/stream')) {
        // Playwright cannot reliably simulate fetch() SSE; exercise JSON fallback instead.
        await route.fulfill({
          status: 503,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Stream unavailable in e2e mock.' }),
        });
        return;
      }
      if (route.request().method() !== 'POST') {
        await route.fallback();
        return;
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(TUTOR_DONE),
      });
    });
  });

  test('user can send a message and see reply with sources', async ({ page }) => {
    await page.goto('/tutor');
    await expect(page.getByRole('heading', { name: /AI Civic Tutor|civic tutor/i })).toBeVisible();

    await page.getByPlaceholder(/ask a civic/i).fill('What is civic education?');
    await page.getByRole('button', { name: /^send$/i }).click();

    await expect(page.getByText(/Civic education helps citizens/i)).toBeVisible({ timeout: 20_000 });
    await expect(page.getByText(/^Sources$/i)).toBeVisible();
    await expect(page.getByRole('link', { name: /Understanding the Transitional Constitution/i })).toBeVisible();
  });

  test('shows usage meter from API', async ({ page }) => {
    await page.goto('/tutor');
    await expect(page.getByText(/30.*remaining|messages today/i)).toBeVisible({ timeout: 10_000 });
  });
});
