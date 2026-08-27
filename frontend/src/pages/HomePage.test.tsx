import { describe, expect, it, vi } from 'vitest';
import { screen } from '@testing-library/react';
import { HomePage } from './HomePage';
import { renderWithProviders } from '../test/utils';

vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn(() => ({ user: null })),
}));

vi.mock('../context/OrganizationContext', () => ({
  useOrganization: vi.fn(() => ({ isOrgAdmin: false })),
}));

import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import type { AuthContextValue, OrganizationContextValue } from '../types/cep';

const mockedUseAuth = vi.mocked(useAuth);
const mockedUseOrganization = vi.mocked(useOrganization);

describe('HomePage', () => {
  it('renders hero and how-it-works sections for visitors', () => {
    mockedUseAuth.mockReturnValue({ user: null } as AuthContextValue);
    renderWithProviders(<HomePage />);

    expect(screen.getByRole('heading', { level: 1, name: /learn\. engage\. build democracy/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2, name: /how it works/i })).toBeInTheDocument();
    expect(screen.getByText(/explore topics/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /peacebuilding/i })).toHaveAttribute(
      'href',
      '/articles?category=peacebuilding',
    );
    expect(screen.getByRole('link', { name: /human rights/i })).toHaveAttribute(
      'href',
      '/articles?category=human-rights',
    );
    expect(screen.getAllByRole('link', { name: /get started/i })[0]).toHaveAttribute('href', '/register');
    expect(screen.getByRole('link', { name: /set up your organization/i })).toHaveAttribute(
      'href',
      '/register?type=organization',
    );
    expect(screen.getByRole('link', { name: /civic information/i })).toHaveAttribute('href', '/news');
    expect(screen.getByRole('link', { name: /spot misinformation/i })).toHaveAttribute('href', '/awareness');
  });

  it('shows personalized CTAs when logged in', () => {
    mockedUseAuth.mockReturnValue({
      user: { first_name: 'Amina', role: { name: 'citizen' } },
    } as AuthContextValue);
    mockedUseOrganization.mockReturnValue({ isOrgAdmin: true } as OrganizationContextValue);
    renderWithProviders(<HomePage />);

    expect(screen.getByText(/welcome back, amina/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /continue learning/i })).toHaveAttribute('href', '/articles');
    expect(screen.getByRole('link', { name: /my progress/i })).toHaveAttribute('href', '/dashboard');
    expect(screen.queryByRole('link', { name: /^get started$/i })).not.toBeInTheDocument();
  });
});
