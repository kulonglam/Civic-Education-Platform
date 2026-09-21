import { describe, expect, it, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RegisterPage } from './RegisterPage';
import { renderWithProviders } from '../test/utils';

vi.mock('../lib/services', () => ({
  authService: {
    register: vi.fn(),
  },
}));

import { authService } from '../lib/services';
import type { Mock } from 'vitest';

const registerMock = authService.register as Mock;

describe('RegisterPage', () => {
  beforeEach(() => {
    registerMock.mockReset();
  });

  it('renders citizen registration by default', () => {
    renderWithProviders(<RegisterPage />);
    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByText(/individual learner/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/organization name/i)).not.toBeInTheDocument();
    expect(screen.getByLabelText(/^email$/i)).toBeInTheDocument();
    expect(screen.queryByText('CivicHub')).not.toBeInTheDocument();
  });

  it('shows organization name when organization mode is selected', async () => {
    renderWithProviders(<RegisterPage />);
    await userEvent.click(screen.getByRole('button', { name: /organization/i }));
    expect(screen.getByLabelText(/organization name/i)).toBeInTheDocument();
  });

  it('shows success message after citizen registration', async () => {
    registerMock.mockResolvedValueOnce({ data: { message: 'ok' } });
    renderWithProviders(<RegisterPage />);

    await userEvent.type(screen.getByLabelText(/first name/i), 'Jane');
    await userEvent.type(screen.getByLabelText(/last name/i), 'Doe');
    await userEvent.type(screen.getByLabelText(/^email$/i), 'jane@test.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'SecurePass123!');
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'SecurePass123!');
    await userEvent.click(screen.getByRole('button', { name: /sign up/i }));

    await waitFor(() => {
      expect(screen.getAllByText(/registration successful/i).length).toBeGreaterThan(0);
    });
    expect(authService.register).toHaveBeenCalledWith(
      expect.objectContaining({ account_type: 'citizen', email: 'jane@test.com' }),
    );
  });
});
