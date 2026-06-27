import { test, expect } from '@playwright/test';

const API = 'http://127.0.0.1:8000/api';

test.describe('Quiz flow', () => {
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

    await page.route(`${API}/organization/current/`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'org-1',
          name: 'Platform Demo',
          slug: 'platform-demo',
          tagline: 'Demo org',
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
        body: JSON.stringify({ count: 1, results: [] }),
      });
    });

    await page.route(`${API}/organization/mine/`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });
  });

  test('user can view quiz list and open a quiz', async ({ page }) => {
    await page.route(`${API}/quizzes/**`, async (route) => {
      const url = route.request().url();
      if (url.endsWith('/quizzes/') || url.includes('/quizzes/?')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            count: 1,
            next: null,
            previous: null,
            results: [
              {
                id: 'quiz-1',
                title: 'Constitution Quiz',
                description: 'Basics of the constitution',
                passing_score: 70,
                is_active: true,
                questions: [{ id: 'q1' }],
                created_at: '2026-01-01',
              },
            ],
          }),
        });
        return;
      }
      if (url.includes('/quizzes/quiz-1')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'quiz-1',
            title: 'Constitution Quiz',
            description: 'Basics of the constitution',
            passing_score: 70,
            questions: [
              {
                id: 'q1',
                question_text: 'South Sudan is a republic?',
                question_type: 'true_false',
                options: [],
                points: 1,
                order: 1,
              },
            ],
          }),
        });
        return;
      }
      await route.continue();
    });

    await page.goto('/quizzes');
    await expect(page.getByText('Constitution Quiz')).toBeVisible();
    await page.getByRole('link', { name: /start quiz/i }).click();
    await expect(page.getByText(/south sudan is a republic/i)).toBeVisible();
  });
});
