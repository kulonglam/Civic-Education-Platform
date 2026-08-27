import { describe, expect, it, vi } from 'vitest';
import { screen } from '@testing-library/react';
import { GuestSaveCta } from './GuestSaveCta';
import { renderWithProviders } from '../test/utils';

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({ user: null }),
}));

describe('GuestSaveCta', () => {
  it('links guests to register and login with return path', () => {
    renderWithProviders(<GuestSaveCta />, { route: '/articles/abc' });
    expect(screen.getByText(/create a free account to save progress/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /create a free account/i })).toHaveAttribute(
      'href',
      '/register',
    );
    expect(screen.getByRole('link', { name: /log in/i })).toHaveAttribute('href', '/login');
  });
});
