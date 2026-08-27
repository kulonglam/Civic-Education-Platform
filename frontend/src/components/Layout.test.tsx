import { describe, expect, it, vi } from 'vitest';
import { screen, within } from '@testing-library/react';
import { Route, Routes } from 'react-router-dom';
import { Layout } from './Layout';
import { renderWithProviders } from '../test/utils';
import { useAuth } from '../context/AuthContext';
import type { AuthContextValue, OrganizationContextValue } from '../types/cep';

vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn(),
}));

vi.mock('../context/OrganizationContext', () => ({
  useOrganization: vi.fn(),
}));

vi.mock('../hooks/useNotificationSocket', () => ({
  useNotificationSocket: () => false,
}));

vi.mock('../hooks/useDarkMode', () => ({
  useDarkMode: () => [false, vi.fn()],
}));

vi.mock('./ApiWakeBanner', () => ({ ApiWakeBanner: () => null }));
vi.mock('./OfflineBanner', () => ({ OfflineBanner: () => null }));
vi.mock('./EmailVerifyBanner', () => ({ EmailVerifyBanner: () => null }));
vi.mock('./InstallPrompt', () => ({ InstallPrompt: () => null }));
vi.mock('./PushNotificationPrompt', () => ({ PushNotificationPrompt: () => null }));
vi.mock('./QuotaBanner', () => ({ QuotaBanner: () => null }));

import { useOrganization } from '../context/OrganizationContext';

const mockedUseAuth = vi.mocked(useAuth);
const mockedUseOrganization = vi.mocked(useOrganization);

function authValue(partial: Partial<AuthContextValue> = {}): AuthContextValue {
  return {
    user: null,
    loading: false,
    impersonation: null,
    login: vi.fn(),
    logout: vi.fn(),
    refreshUser: vi.fn(),
    verifyMfaLogin: vi.fn(),
    startImpersonation: vi.fn(),
    exitImpersonation: vi.fn(),
    hasRole: () => false,
    isPlatformAdmin: () => false,
    isSuperAdmin: () => false,
    ...partial,
  };
}

function orgValue(
  partial: Partial<OrganizationContextValue> = {},
): OrganizationContextValue {
  return {
    organization: null,
    membership: null,
    loading: false,
    refresh: vi.fn(),
    isOrgAdmin: false,
    isOrgContentManager: false,
    isOrgModerator: false,
    ...partial,
  };
}

function renderLayout(route: string) {
  mockedUseAuth.mockReturnValue(authValue());
  mockedUseOrganization.mockReturnValue(orgValue());
  return renderWithProviders(
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<div>home</div>} />
        <Route path="/login" element={<div>login body</div>} />
        <Route path="/register" element={<div>register body</div>} />
        <Route path="/forgot-password" element={<div>forgot body</div>} />
      </Route>
    </Routes>,
    { route },
  );
}

describe('Layout header brand', () => {
  it.each(['/', '/login', '/register', '/forgot-password'])(
    'shows the navbar logo and name on %s',
    (route) => {
      renderLayout(route);
      const header = screen.getByRole('banner');
      expect(within(header).getByText('Civic Education RSS')).toBeInTheDocument();
      expect(within(header).getByText('Building informed citizens')).toBeInTheDocument();
      expect(
        within(header).getByRole('link', { name: 'Civic Education RSS' }),
      ).toHaveAttribute('href', '/');
    },
  );
});
