import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';

const mockUser = {
  id: '1',
  email: 'user@test.com',
  first_name: 'Test',
  last_name: 'User',
  role: { id: 1, name: 'citizen' },
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

const mockedUseAuth = vi.mocked(useAuth);

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
    mockedUseAuth.mockReturnValue({
      user: null,
      loading: true,
      login: vi.fn(),
      logout: vi.fn(),
      refreshUser: vi.fn(),
      hasRole: () => false,
    });
    renderProtected();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('redirects unauthenticated users to login', () => {
    mockedUseAuth.mockReturnValue({
      user: null,
      loading: false,
      login: vi.fn(),
      logout: vi.fn(),
      refreshUser: vi.fn(),
      hasRole: () => false,
    });
    renderProtected();
    expect(screen.getByText('Login page')).toBeInTheDocument();
  });

  it('renders children for authenticated users', () => {
    mockedUseAuth.mockReturnValue({
      user: mockUser,
      loading: false,
      login: vi.fn(),
      logout: vi.fn(),
      refreshUser: vi.fn(),
      hasRole: () => true,
    });
    renderProtected();
    expect(screen.getByText('Secret content')).toBeInTheDocument();
  });

  it('blocks users without required role', () => {
    mockedUseAuth.mockReturnValue({
      user: mockUser,
      loading: false,
      login: vi.fn(),
      logout: vi.fn(),
      refreshUser: vi.fn(),
      hasRole: () => false,
    });
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
});
