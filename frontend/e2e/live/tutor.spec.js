import { test, expect } from '@playwright/test';
import { LIVE_API, liveAuthHeaders, loginLive, seedLiveAuth } from '../helpers';

test.describe('Live AI tutor API', () => {
  test('POST /tutor/chat/ returns reply and sources array', async ({ request }) => {
    const tokens = await loginLive(request);

    const response = await request.post(`${LIVE_API}/tutor/chat/`, {
      headers: liveAuthHeaders(tokens),
      data: { message: 'What is the Transitional Constitution?' },
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.reply).toBeTruthy();
    expect(Array.isArray(body.sources)).toBeTruthy();
    expect(body).toHaveProperty('messages_used_today');
    expect(body).toHaveProperty('session_id');
  });

  test('POST /tutor/chat/stream/ returns SSE done event', async ({ request }) => {
    const tokens = await loginLive(request);

    const response = await request.post(`${LIVE_API}/tutor/chat/stream/`, {
      headers: {
        ...liveAuthHeaders(tokens),
        Accept: 'text/event-stream',
      },
      data: { message: 'Explain civic rights briefly.' },
    });

    expect(response.ok()).toBeTruthy();
    expect(response.headers()['content-type']).toContain('text/event-stream');
    const body = await response.text();
    expect(body).toMatch(/event: (token|done)/);
    expect(body).toContain('event: done');
  });

  test('GET /tutor/usage/platform/ is admin-only aggregate', async ({ request }) => {
    const tokens = await loginLive(request);

    const response = await request.get(`${LIVE_API}/tutor/usage/platform/`, {
      headers: liveAuthHeaders(tokens),
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body).toHaveProperty('messages_today');
    expect(body).toHaveProperty('tokens_today');
    expect(body).toHaveProperty('active_users_today');
  });
});

test.describe('Live AI tutor UI', () => {
  test('authenticated user can chat on /tutor', async ({ page, request }) => {
    const tokens = await loginLive(request);
    await seedLiveAuth(page, tokens);

    await page.goto('/tutor');
    await expect(page.getByRole('heading', { name: /AI Civic Tutor|civic tutor/i })).toBeVisible({
      timeout: 15_000,
    });

    await page.getByPlaceholder(/ask a civic/i).fill('What is civic education?');
    await page.getByRole('button', { name: /send/i }).click();

    // Dev stub or real Claude reply — either way the assistant bubble should appear.
    await expect(
      page.locator('.rounded-2xl').filter({ hasText: /civic|constitution|development response/i }).first(),
    ).toBeVisible({ timeout: 25_000 });
  });
});
