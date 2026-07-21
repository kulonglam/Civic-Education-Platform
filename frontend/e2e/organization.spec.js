import { test, expect } from '@playwright/test';
import { apiGlob, mockSession } from './helpers';

test.describe('Organization enterprise settings', () => {
  test.beforeEach(async ({ page }) => {
    await mockSession(
      page,
      {
        email: 'owner@test.com',
        first_name: 'Org',
        last_name: 'Owner',
        role: { id: 1, name: 'citizen' },
        mfa_required: false,
      },
      {
        memberRole: 'owner',
        organization: {
          id: 'org-1',
          name: 'Test Org',
          slug: 'test-org',
          force_mfa_for_admins: true,
          audit_retention_days: 365,
          ip_allowlist: [],
        },
      }
    );

    // Register after mockSession so these handlers win for enterprise endpoints.
    await page.route(apiGlob('organization/**'), async (route) => {
      const url = route.request().url();
      // Let current/members/mine keep mockSession handlers (first match wins).
      if (
        url.includes('/organization/current') ||
        url.includes('/organization/members') ||
        url.includes('/organization/mine')
      ) {
        await route.fallback();
        return;
      }
      if (
        url.includes('/departments') ||
        url.includes('/scim/') ||
        url.includes('/support/') ||
        url.includes('/sso') ||
        url.includes('/invites')
      ) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        });
        return;
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({}),
      });
    });

    await page.route(apiGlob('billing/**'), async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ subscription: null }),
      });
    });

    await page.route(apiGlob('notify/**'), async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });
  });

  test('org admin can switch settings tabs', async ({ page }) => {
    await page.goto('/organization');
    await expect(page.getByRole('heading', { name: /organization settings/i })).toBeVisible();

    const securityTab = page.getByRole('tab', { name: /security/i });
    await expect(securityTab).toBeVisible();
    await securityTab.click();
    await expect(page.getByText(/enterprise sso/i)).toBeVisible();

    await page.getByRole('tab', { name: /people/i }).click();
    await expect(page.getByText(/invite/i).first()).toBeVisible();
  });
});
