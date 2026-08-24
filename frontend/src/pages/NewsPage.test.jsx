import { describe, expect, it, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { NewsPage } from './NewsPage';
import { renderWithProviders } from '../test/utils';

vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn(() => ({ user: null, hasRole: () => false })),
}));

vi.mock('../context/OrganizationContext', () => ({
  useOrganization: vi.fn(() => ({ isOrgContentManager: false })),
}));

vi.mock('../lib/services', () => ({
  newsService: {
    list: vi.fn().mockResolvedValue({
      data: {
        count: 2,
        results: [
          {
            id: 'n1',
            title: 'Constitution remains supreme law',
            body: 'A verified restatement of the Transitional Constitution.',
            topic: 'law_policy',
            claim_type: 'verified_fact',
            source_name: 'Transitional Constitution, 2011',
            published_at: '2026-08-01T00:00:00Z',
          },
          {
            id: 'n2',
            title: 'Forwarded polling rumour',
            body: 'An unconfirmed message about polling hours.',
            topic: 'election',
            claim_type: 'unverified',
            published_at: '2026-08-02T00:00:00Z',
          },
        ],
      },
    }),
  },
}));

describe('NewsPage', () => {
  it('shows the claim-type legend and labelled news cards', async () => {
    renderWithProviders(<NewsPage />);

    expect(screen.getByRole('heading', { name: /how we label information/i })).toBeInTheDocument();
    expect(screen.getByText(/checked against a named source/i)).toBeInTheDocument();
    expect(screen.getByText(/teaches a civic idea/i)).toBeInTheDocument();
    expect(screen.getByText(/view or commentary/i)).toBeInTheDocument();
    expect(screen.getByText(/not confirmed/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByRole('link', { name: /constitution remains supreme law/i })).toHaveAttribute(
        'href',
        '/news/n1',
      );
    });
    expect(screen.getAllByText('Verified fact').length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText('Unverified information').length).toBeGreaterThanOrEqual(2);
    expect(screen.getByRole('link', { name: /forwarded polling rumour/i })).toHaveAttribute(
      'href',
      '/news/n2',
    );
  });
});
