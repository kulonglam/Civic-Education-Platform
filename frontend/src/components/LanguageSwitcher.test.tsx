import { describe, expect, it, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LanguageSwitcher } from './LanguageSwitcher';
import { renderWithProviders } from '../test/utils';
import i18n from '../i18n';

const mockRefreshUser = vi.fn();
const mockUpdateProfile = vi.fn().mockResolvedValue({ data: {} });

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: { id: '1', profile: { preferred_language: 'en' } },
    refreshUser: mockRefreshUser,
  }),
}));

vi.mock('../lib/services', () => ({
  userService: {
    updateProfile: (...args: unknown[]) => mockUpdateProfile(...args),
  },
}));

describe('LanguageSwitcher', () => {
  beforeEach(async () => {
    mockUpdateProfile.mockClear();
    mockRefreshUser.mockClear();
    await i18n.changeLanguage('en');
  });

  it('persists language preference for signed-in users', async () => {
    renderWithProviders(<LanguageSwitcher />);
    await userEvent.click(screen.getByRole('button', { name: /switch language/i }));
    await waitFor(() => {
      expect(mockUpdateProfile).toHaveBeenCalledWith({ preferred_language: 'ar' });
    });
  });
});
