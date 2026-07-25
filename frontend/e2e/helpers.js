/**
 * Shared Playwright helpers for mocked (non-live) e2e.
 * Matches frontend/.env (VITE_API_BASE_URL → …/api); backend also aliases /api/v1.
 * JWT lives in memory + sessionStorage flag (not localStorage).
 */
export const API = process.env.E2E_API_BASE ?? 'http://127.0.0.1:8000/api';

/** Match both /api/… and /api/v1/… paths. */
export const apiGlob = (suffix) => `**/api/**/${suffix}`;

export const LIVE_API = process.env.E2E_API_URL
  ? `${process.env.E2E_API_URL}/api`
  : 'http://127.0.0.1:8000/api';

export const LIVE_ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL ?? 'admin@civic-education.ss';
export const LIVE_ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD ?? 'AdminPass123!';
export const LIVE_ORG_SLUG = process.env.E2E_ORG_SLUG ?? 'platform-demo';

/**
 * Log in against the live backend (e2e-live job).
 * @param {import('@playwright/test').APIRequestContext} request
 */
export async function loginLive(
  request,
  email = LIVE_ADMIN_EMAIL,
  password = LIVE_ADMIN_PASSWORD,
) {
  const response = await request.post(`${LIVE_API}/auth/login/`, {
    data: { email, password },
  });
  if (!response.ok()) {
    throw new Error(`Live login failed (${response.status()}): ${await response.text()}`);
  }
  return response.json();
}

/**
 * Seed JWT + org slug in the browser before navigation (live e2e).
 * @param {import('@playwright/test').Page} page
 */
export async function seedLiveAuth(page, tokens, orgSlug = LIVE_ORG_SLUG) {
  await page.addInitScript(({ access, slug }) => {
    localStorage.setItem('cep_access', access);
    localStorage.setItem('cep_refresh', 'refresh-not-needed-for-read');
    localStorage.setItem('cep_org_slug', slug);
    sessionStorage.setItem('cep_session', '1');
  }, { access: tokens.access, slug: orgSlug });
}

/**
 * Default auth headers for live API calls.
 */
export function liveAuthHeaders(tokens, orgSlug = LIVE_ORG_SLUG) {
  return {
    Authorization: `Bearer ${tokens.access}`,
    'X-Tenant-Slug': orgSlug,
  };
}

/**
 * @param {import('@playwright/test').Page} page
 * @param {object} [profileOverrides]
 * @param {object} [options]
 * @param {object[]} [options.members] - organization/members results (drives isOrgAdmin)
 */
export async function mockSession(page, profileOverrides = {}, options = {}) {
  const profile = {
    id: '1',
    email: 'user@test.com',
    first_name: 'Test',
    last_name: 'User',
    role: { id: 1, name: 'citizen' },
    is_active: true,
    email_verified: true,
    created_at: '2026-01-01',
    profile: { bio: '', avatar_url: '', preferred_language: 'en' },
    ...profileOverrides,
  };

  const members = options.members ?? [
    {
      id: 'm1',
      user: profile.id,
      user_email: profile.email,
      user_name: `${profile.first_name} ${profile.last_name}`.trim(),
      role: options.memberRole ?? 'member',
      created_at: '2026-01-01',
    },
  ];

  await page.addInitScript(() => {
    sessionStorage.setItem('cep_session', '1');
    localStorage.setItem('cep_org_slug', 'platform-demo');
  });

  await page.route(apiGlob('auth/token/refresh/**'), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        access: 'fake-access-token',
        refresh: 'fake-refresh-token',
      }),
    });
  });

  // Profile without Bearer must fail so AuthContext runs refresh and stores access token
  // (OrganizationContext requires tokenStore.access).
  await page.route(apiGlob('users/profile/**'), async (route) => {
    const auth = route.request().headers().authorization || '';
    if (!auth.toLowerCase().startsWith('bearer ')) {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Authentication credentials were not provided.' }),
      });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(profile),
    });
  });

  await page.route(apiGlob('organization/current/**'), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'org-1',
        name: 'Platform Demo',
        slug: 'platform-demo',
        tagline: 'Building informed citizens',
        logo_url: '',
        primary_color: '#059669',
        is_active: true,
        created_at: '2026-01-01',
        ...(options.organization || {}),
      }),
    });
  });

  await page.route(apiGlob('organization/members/**'), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ count: members.length, results: members }),
    });
  });

  await page.route(apiGlob('organization/mine/**'), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(
        members.map((m) => ({
          id: m.id,
          role: m.role,
          organization: {
            id: 'org-1',
            name: options.organization?.name || 'Platform Demo',
            slug: options.organization?.slug || 'platform-demo',
            tagline: '',
            logo_url: '',
            primary_color: '#059669',
            is_active: true,
            created_at: '2026-01-01',
          },
          created_at: '2026-01-01',
        }))
      ),
    });
  });
}
