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

describe('HomePage', () => {
  it('renders hero and how-it-works sections for visitors', () => {
    useAuth.mockReturnValue({ user: null });
    renderWithProviders(<HomePage />);

    expect(screen.getByRole('heading', { level: 1, name: /learn\. engage\. build democracy/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2, name: /how it works/i })).toBeInTheDocument();
    expect(screen.getAllByRole('link', { name: /get started/i })[0]).toHaveAttribute('href', '/register');
    expect(screen.getByRole('link', { name: /set up your organization/i })).toHaveAttribute(
      'href',
      '/register?type=organization',
    );
  });

  it('shows personalized CTAs when logged in', () => {
    useAuth.mockReturnValue({
      user: { first_name: 'Amina', role: { name: 'citizen' } },
    });
    useOrganization.mockReturnValue({ isOrgAdmin: true });
    renderWithProviders(<HomePage />);

    expect(screen.getByText(/welcome back, amina/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /continue learning/i })).toHaveAttribute('href', '/articles');
    expect(screen.getByRole('link', { name: /go to dashboard/i })).toHaveAttribute('href', '/dashboard');
    expect(screen.queryByRole('link', { name: /^get started$/i })).not.toBeInTheDocument();
  });
});
