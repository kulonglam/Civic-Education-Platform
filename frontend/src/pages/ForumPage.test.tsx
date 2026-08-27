import { describe, expect, it, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { ForumPage } from './ForumPage';
import { renderWithProviders } from '../test/utils';

vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn(() => ({ user: null, hasRole: () => false })),
}));

vi.mock('../lib/services', () => ({
  forumService: {
    listTopics: vi.fn().mockResolvedValue({
      data: {
        count: 2,
        results: [
          {
            id: 't1',
            title: 'How can youth participate in local governance?',
            content: 'Share practical examples from your payam.',
            kind: 'discussion',
            board: 'governance',
            author_name: 'Admin User',
            comment_count: 1,
            is_approved: true,
            created_at: '2026-08-01T00:00:00Z',
          },
          {
            id: 't2',
            title: 'What is one peaceful way to check a rumour about an election?',
            content: 'Name an official source before you share.',
            kind: 'question',
            board: 'elections',
            author_name: 'Admin User',
            comment_count: 1,
            is_approved: true,
            created_at: '2026-08-02T00:00:00Z',
          },
        ],
      },
    }),
  },
  engagementService: {
    polls: vi.fn().mockResolvedValue({ data: [] }),
  },
}));

describe('ForumPage', () => {
  it('shows moderation guidelines, boards, and Q&A topics', async () => {
    renderWithProviders(<ForumPage />);

    expect(screen.getByRole('heading', { name: /moderated civic discussion/i })).toBeInTheDocument();
    expect(screen.getByText(/hate speech, harassment, misinformation, and political manipulation/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByRole('link', { name: /youth participate in local governance/i })).toHaveAttribute(
        'href',
        '/forum/t1',
      );
    });
    expect(screen.getByRole('link', { name: /peaceful way to check a rumour/i })).toHaveAttribute(
      'href',
      '/forum/t2',
    );
    expect(screen.getAllByText('Discussion').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Question').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Governance').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Elections').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByLabelText(/type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/topic/i)).toBeInTheDocument();
  });
});
