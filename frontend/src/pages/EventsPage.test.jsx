import { describe, expect, it, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { EventsPage } from './EventsPage';
import { renderWithProviders } from '../test/utils';

vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn(() => ({ user: null, hasRole: () => false })),
}));

vi.mock('../context/OrganizationContext', () => ({
  useOrganization: vi.fn(() => ({ isOrgContentManager: false })),
}));

vi.mock('../lib/services', () => ({
  eventsService: {
    list: vi.fn().mockResolvedValue({
      data: {
        count: 1,
        results: [
          {
            id: 'e1',
            title: 'County budget public hearing',
            description: 'Ask how county funds are allocated.',
            kind: 'public_hearing',
            starts_at: '2026-11-12T07:00:00Z',
            location: 'County hall',
            status: 'published',
          },
        ],
      },
    }),
  },
}));

describe('EventsPage', () => {
  it('shows the civic calendar and upcoming events', async () => {
    renderWithProviders(<EventsPage />);

    expect(screen.getByRole('heading', { name: /civic events/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/filter by event type/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getAllByRole('link', { name: /county budget public hearing/i }).length).toBeGreaterThan(0);
    });
    expect(screen.getByRole('heading', { name: /upcoming/i })).toBeInTheDocument();
  });
});
