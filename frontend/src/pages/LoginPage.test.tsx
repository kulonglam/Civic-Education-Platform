import { describe, expect, it, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import { LoginPage } from './LoginPage';
import { renderWithProviders } from '../test/utils';

const mockLogin = vi.fn();
const mockNavigate = vi.fn();

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({ login: mockLogin, verifyMfaLogin: vi.fn() }),
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ state: null }),
  };
});

vi.mock('../lib/services', () => ({
  authService: {
    ssoStatus: vi.fn().mockResolvedValue({ data: { configured: false, enabled_for_org: false } }),
  },
}));

describe('LoginPage', () => {
  beforeEach(() => {
    mockLogin.mockReset();
    mockNavigate.mockReset();
  });

  it('renders login form fields', () => {
    renderWithProviders(<LoginPage />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument();
    expect(screen.queryByText('Civic Education RSS')).not.toBeInTheDocument();
  });

  it('shows error when login fails', async () => {
    mockLogin.mockRejectedValueOnce(
      new axios.AxiosError('Unauthorized', '401', undefined, undefined, {
        status: 401,
        statusText: 'Unauthorized',
        headers: {},
        config: { headers: new axios.AxiosHeaders() },
        data: { detail: 'Invalid credentials.' },
      })
    );
    renderWithProviders(<LoginPage />);
    await userEvent.type(screen.getByLabelText(/email/i), 'bad@test.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'wrong');
    await userEvent.click(screen.getByRole('button', { name: /log in/i }));
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });

  it('navigates home after successful login', async () => {
    mockLogin.mockResolvedValueOnce(undefined);
    renderWithProviders(<LoginPage />);
    await userEvent.type(screen.getByLabelText(/email/i), 'user@test.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'TestPass123!');
    await userEvent.click(screen.getByRole('button', { name: /log in/i }));
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('user@test.com', 'TestPass123!');
      expect(mockNavigate).toHaveBeenCalledWith('/', { replace: true });
    });
  });
});
