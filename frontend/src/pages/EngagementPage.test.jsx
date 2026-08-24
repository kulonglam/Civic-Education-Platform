import { describe, expect, it, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { EngagementPage } from './EngagementPage';
import { renderWithProviders } from '../test/utils';

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({ hasRole: () => false }),
}));
vi.mock('../context/OrganizationContext', () => ({
  useOrganization: () => ({ isOrgContentManager: false }),
}));
vi.mock('../lib/services', () => ({
  engagementService: {
    polls: vi.fn().mockResolvedValue({
      data: [
        {
          id: 'p1',
          question: 'What is the biggest challenge in your community?',
          description: 'A community poll.',
          kind: 'community',
          is_open: true,
          total_votes: 8,
          results_visible: false,
          options: [
            { id: 'o1', label: 'Education' },
            { id: 'o2', label: 'Health services' },
          ],
        },
        {
          id: 'p2',
          question: 'Do citizens understand this new policy?',
          kind: 'educational',
          is_open: true,
          total_votes: 8,
          results_visible: false,
          options: [
            { id: 'o3', label: 'I understand it clearly' },
            { id: 'o4', label: 'I do not understand it' },
          ],
        },
      ],
    }),
    petitions: vi.fn().mockResolvedValue({ data: [] }),
    campaigns: vi.fn().mockResolvedValue({ data: [] }),
    votePoll: vi.fn(),
    joinCampaign: vi.fn(),
  },
}));

describe('EngagementPage', () => {
  it('shows educational and community polls with response counts', async () => {
    renderWithProviders(<EngagementPage />);

    expect(await screen.findByText(/educational polls check civic understanding/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText(/biggest challenge in your community/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/do citizens understand this new policy/i)).toBeInTheDocument();
    expect(screen.getAllByText('Community').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Educational').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/8 responses/i).length).toBeGreaterThanOrEqual(2);
  });
});
