import { beforeEach, describe, expect, it, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { EventsDetailPage } from './EventsDetailPage';
import { renderWithProviders } from '../test/utils';

const { event, register, reminder, calendar } = vi.hoisted(() => {
  const event = {
    id: 'e1',
    title: 'Payam community meeting on local services',
    description: 'Neighbours meet chiefs and county officers.',
    kind: 'community_meeting',
    starts_at: '2026-09-26T12:00:00Z',
    location: 'Munuki payam compound',
    status: 'published',
    allows_registration: true,
    user_registered: false,
    user_reminder: false,
    google_calendar_url: 'https://calendar.google.com/calendar/render?action=TEMPLATE',
  };
  return {
    event,
    register: vi.fn(),
    reminder: vi.fn(),
    calendar: vi.fn(),
  };
});

vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn(() => ({
    user: { id: 'u1' },
    hasRole: () => false,
  })),
}));

vi.mock('../context/OrganizationContext', () => ({
  useOrganization: vi.fn(() => ({ isOrgContentManager: false })),
}));

vi.mock('../lib/services', () => ({
  eventsService: {
    get: vi.fn().mockResolvedValue({ data: event }),
    register,
    reminder,
    calendar,
  },
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ id: 'e1' }),
  };
});

describe('EventsDetailPage', () => {
  beforeEach(() => {
    URL.createObjectURL = vi.fn(() => 'blob:event');
    URL.revokeObjectURL = vi.fn();
    register.mockResolvedValue({ data: { ...event, user_registered: true } });
    reminder.mockResolvedValue({ data: { ...event, user_registered: true, user_reminder: true } });
    calendar.mockResolvedValue({ data: new Blob(['BEGIN:VCALENDAR'], { type: 'text/calendar' }) });
  });

  it('lets a member register, set a reminder, and add the event to a calendar', async () => {
    const user = userEvent.setup();
    renderWithProviders(<EventsDetailPage />, { route: '/events/e1' });

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /payam community meeting/i })).toBeInTheDocument();
    });
    expect(screen.getByRole('link', { name: /add to google calendar/i })).toHaveAttribute(
      'href',
      event.google_calendar_url,
    );

    await user.click(screen.getByRole('button', { name: /register for event/i }));
    expect(register).toHaveBeenCalledWith('e1', true);

    await user.click(screen.getByRole('button', { name: /set reminder/i }));
    expect(reminder).toHaveBeenCalledWith('e1', true);

    await user.click(screen.getByRole('button', { name: /download calendar file/i }));
    expect(calendar).toHaveBeenCalledWith('e1');
  });
});
