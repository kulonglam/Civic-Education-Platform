import { describe, expect, it, vi } from 'vitest';
import { screen } from '@testing-library/react';
import { BillingPage } from './BillingPage';
import { renderWithProviders } from '../test/utils';

vi.mock('../context/OrganizationContext', () => ({
  useOrganization: () => ({ isOrgAdmin: true }),
}));

vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQuery: ({ queryKey }) => {
      if (queryKey[0] === 'plans') {
        return {
          data: [
            {
              id: '1',
              code: 'free',
              name: 'Free',
              price_cents: 0,
              currency: 'USD',
              interval: 'month',
              max_members: 5,
              max_articles: 10,
              max_quizzes: 5,
            },
          ],
          isLoading: false,
        };
      }
      return {
        data: {
          subscription: {
            plan: { code: 'free', name: 'Free' },
            status: 'active',
          },
          usage: {
            members: { used: 2, limit: 5 },
            articles: { used: 3, limit: 10 },
            quizzes: { used: 1, limit: 5 },
          },
        },
        isLoading: false,
      };
    },
    useMutation: () => ({ mutate: vi.fn(), isPending: false }),
  };
});

describe('BillingPage', () => {
  it('renders current plan and available plans', () => {
    renderWithProviders(<BillingPage />);
    expect(screen.getByText(/billing & plans/i)).toBeInTheDocument();
    expect(screen.getAllByText('Free').length).toBeGreaterThan(0);
    expect(screen.getByText(/manage billing/i)).toBeInTheDocument();
  });
});
