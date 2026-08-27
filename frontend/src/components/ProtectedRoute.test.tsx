import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';

const mockUser = {
  id: '1',
  email: 'user@test.com',
  first_name: 'Test',
  last_name: 'User',
  role: { id: '1', name: 'citizen' },
  is_active: true,
  email_verified: true,
  created_at: '2026-01-01',
  profile: { bio: '', avatar_url: '', preferred_language: 'en' },
};

vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn(),
}));

vi.mock('../context/OrganizationContext', () => ({
  useOrganization: vi.fn(() => ({
    membership: { role: 'member' },
    loading: false,
    organization: null,
    isOrgAdmin: false,
  })),
}));

import { useAuth } from '../context/AuthContext';
import type { AuthContextValue } from '../types/cep';

const mockedUseAuth = vi.mocked(useAuth);

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

function renderProtected(initialPath = '/private') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route
          path="/private"
          element={
            <ProtectedRoute>
              <div>Secret content</div>
            </ProtectedRoute>
          }
        />
        <Route path="/login" element={<div>Login page</div>} />
        <Route path="/" element={<div>Home</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('ProtectedRoute', () => {
  it('shows spinner while loading', () => {
    mockedUseAuth.mockReturnValue(
      authValue({
        user: null,
        loading: true,
      }),
    );
    renderProtected();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('redirects unauthenticated users to login', () => {
    mockedUseAuth.mockReturnValue(
      authValue({
        user: null,
        loading: false,
      }),
    );
    renderProtected();
    expect(screen.getByText('Login page')).toBeInTheDocument();
  });

  it('renders children for authenticated users', () => {
    mockedUseAuth.mockReturnValue(
      authValue({
        user: mockUser,
        loading: false,
        hasRole: () => true,
      }),
    );
    renderProtected();
    expect(screen.getByText('Secret content')).toBeInTheDocument();
  });

  it('blocks users without required role', () => {
    mockedUseAuth.mockReturnValue(
      authValue({
        user: mockUser,
        loading: false,
        hasRole: () => false,
      }),
    );
    render(
      <MemoryRouter initialEntries={['/admin-only']}>
        <Routes>
          <Route
            path="/admin-only"
            element={
              <ProtectedRoute roles={['admin']}>
                <div>Admin panel</div>
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<div>Home</div>} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText('Home')).toBeInTheDocument();
  });

  it('allows Super Admin on Administrator-only routes', () => {
    mockedUseAuth.mockReturnValue(
      authValue({
        user: { ...mockUser, role: { id: '2', name: 'super_admin' } },
        loading: false,
        hasRole: () => true,
      }),
    );
    render(
      <MemoryRouter initialEntries={['/admin-only']}>
        <Routes>
          <Route
            path="/admin-only"
            element={
              <ProtectedRoute roles={['admin']}>
                <div>Admin panel</div>
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<div>Home</div>} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText('Admin panel')).toBeInTheDocument();
  });
});
