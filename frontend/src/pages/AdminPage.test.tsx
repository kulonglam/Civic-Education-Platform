import { describe, expect, it, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AdminPage } from './AdminPage';
import { renderWithProviders } from '../test/utils';

const mockIsPlatformAdmin = vi.fn();
const mockHasRole = vi.fn();

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: { id: '1', role: { name: 'moderator' }, first_name: 'Mod' },
    hasRole: (...roles: string[]) => mockHasRole(...roles),
    isPlatformAdmin: () => mockIsPlatformAdmin(),
    isSuperAdmin: () => false,
  }),
}));

vi.mock('../context/OrganizationContext', () => ({
  useOrganization: () => ({
    membership: null,
    isOrgAdmin: false,
    isOrgModerator: false,
    isOrgContentManager: false,
    loading: false,
  }),
}));

vi.mock('../lib/services', () => ({
  forumService: {
    pending: vi.fn().mockResolvedValue({ data: { topics: [], comments: [], reports: [] } }),
    reviewReport: vi.fn(),
  },
  userService: { list: vi.fn().mockResolvedValue({ data: { results: [] } }) },
  analyticsService: {
    overview: vi.fn().mockResolvedValue({ data: { total_users: 1 } }),
    quizzes: vi.fn().mockResolvedValue({ data: [] }),
    forum: vi.fn().mockResolvedValue({ data: {} }),
    polls: vi.fn().mockResolvedValue({ data: { total_polls: 0, total_responses: 0, polls: [] } }),
    learning: vi.fn().mockResolvedValue({ data: {} }),
  },
  notificationService: {
    pushStats: vi.fn().mockResolvedValue({ data: { total_subscriptions: 0, users_with_push: 0 } }),
  },
  auditService: { logs: vi.fn().mockResolvedValue({ data: { results: [] } }) },
  notifyService: { platformBroadcast: vi.fn(), platformWhatsAppBroadcast: vi.fn() },
  organizationService: {
    platformOrgs: vi.fn().mockResolvedValue({ data: { results: [] } }),
    platformOrgDetail: vi.fn().mockResolvedValue({ data: {} }),
    setOrgActive: vi.fn().mockResolvedValue({ data: {} }),
    platformUsage: vi.fn().mockResolvedValue({ data: { totals: {}, organizations: [] } }),
    platformSlo: vi.fn().mockResolvedValue({ data: {} }),
    platformSupportCases: vi.fn().mockResolvedValue({ data: { results: [] } }),
    assignOrgPlan: vi.fn().mockResolvedValue({ data: {} }),
  },
  billingService: {
    plans: vi.fn().mockResolvedValue({ data: { results: [] } }),
  },
  securityService: {
    events: vi.fn().mockResolvedValue({ data: { results: [] } }),
  },
  awarenessService: {
    listReports: vi.fn().mockResolvedValue({ data: [] }),
    reviewReport: vi.fn(),
  },
}));

describe('AdminPage', () => {
  beforeEach(() => {
    mockIsPlatformAdmin.mockReturnValue(false);
    mockHasRole.mockImplementation((...roles) => roles.includes('moderator'));
  });

  it('shows moderation guidance for non-platform admins', async () => {
    renderWithProviders(<AdminPage />);
    expect(await screen.findByText(/recommended user roles/i)).toBeInTheDocument();
    expect(screen.getByText(/platform analytics and role assignment/i)).toBeInTheDocument();
  });

  it('uses platform admin title when user is platform admin', async () => {
    mockIsPlatformAdmin.mockReturnValue(true);
    mockHasRole.mockImplementation((...roles) => roles.includes('admin'));
    renderWithProviders(<AdminPage />);
    expect(await screen.findByRole('heading', { name: /platform administration/i })).toBeInTheDocument();
  });

  it('shows content management links for editors', async () => {
    mockHasRole.mockImplementation((...roles) => roles.includes('editor'));
    renderWithProviders(<AdminPage />);
    expect(await screen.findByRole('heading', { name: /content administration/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /create a lesson/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /create a quiz/i })).toBeInTheDocument();
    expect(screen.queryByText(/moderation queue/i)).not.toBeInTheDocument();
  });

  it('splits platform admin into tabs', async () => {
    const user = userEvent.setup();
    mockIsPlatformAdmin.mockReturnValue(true);
    mockHasRole.mockImplementation((...roles) => roles.includes('admin'));
    renderWithProviders(<AdminPage />);
    expect(await screen.findByRole('tab', { name: /^overview$/i })).toHaveAttribute('aria-selected', 'true');
    expect(screen.queryByRole('link', { name: /create a lesson/i })).not.toBeInTheDocument();
    await user.click(screen.getByRole('tab', { name: /^content$/i }));
    expect(screen.getByRole('link', { name: /create a lesson/i })).toBeInTheDocument();
  });
});
