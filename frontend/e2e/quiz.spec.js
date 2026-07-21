import { test, expect } from '@playwright/test';
import { apiGlob, mockSession } from './helpers';

test.describe('Quiz flow', () => {
  test.beforeEach(async ({ page }) => {
    await mockSession(page);
  });

  test('user can view quiz list and open a quiz', async ({ page }) => {
    await page.route(apiGlob('quizzes/**'), async (route) => {
      const url = new URL(route.request().url());
      const path = url.pathname.replace(/\/+$/, '');
      const detailMatch = path.match(/\/quizzes\/([^/]+)$/);

      if (detailMatch && detailMatch[1] !== 'quizzes') {
        const id = detailMatch[1];
        if (id === 'quiz-1') {
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
      }

      // List: /quizzes or /quizzes/
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
    });

    await page.goto('/quizzes');
    await expect(page.getByText('Constitution Quiz')).toBeVisible();
    await page.getByRole('link', { name: /start quiz/i }).click();
    await expect(page.getByText(/south sudan is a republic/i)).toBeVisible();
  });
});
