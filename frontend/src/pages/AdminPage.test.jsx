import { describe, expect, it, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import { AdminPage } from './AdminPage';
import { renderWithProviders } from '../test/utils';

const mockIsPlatformAdmin = vi.fn();
const mockHasRole = vi.fn();

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: { id: '1', role: { name: 'moderator' }, first_name: 'Mod' },
    hasRole: (...roles) => mockHasRole(...roles),
    isPlatformAdmin: () => mockIsPlatformAdmin(),
  }),
}));

vi.mock('../lib/services', () => ({
  forumService: {
    pending: vi.fn().mockResolvedValue({ data: { topics: [], comments: [] } }),
  },
  userService: { list: vi.fn().mockResolvedValue({ data: { results: [] } }) },
  analyticsService: {
    overview: vi.fn().mockResolvedValue({ data: { total_users: 1 } }),
    quizzes: vi.fn().mockResolvedValue({ data: [] }),
    forum: vi.fn().mockResolvedValue({ data: {} }),
    learning: vi.fn().mockResolvedValue({ data: {} }),
  },
  notificationService: {
    pushStats: vi.fn().mockResolvedValue({ data: { total_subscriptions: 0, users_with_push: 0 } }),
  },
  auditService: { logs: vi.fn().mockResolvedValue({ data: { results: [] } }) },
  notifyService: { platformBroadcast: vi.fn() },
}));

describe('AdminPage', () => {
  beforeEach(() => {
    mockIsPlatformAdmin.mockReturnValue(false);
    mockHasRole.mockImplementation((...roles) => roles.includes('moderator'));
  });

  it('shows moderation guidance for non-platform admins', async () => {
    renderWithProviders(<AdminPage />);
    expect(await screen.findByText(/two layers of access/i)).toBeInTheDocument();
    expect(screen.getByText(/platform analytics and role assignment/i)).toBeInTheDocument();
  });

  it('uses platform admin title when user is platform admin', async () => {
    mockIsPlatformAdmin.mockReturnValue(true);
    mockHasRole.mockImplementation((...roles) => roles.includes('admin'));
    renderWithProviders(<AdminPage />);
    expect(await screen.findByRole('heading', { name: /platform administration/i })).toBeInTheDocument();
  });
});
