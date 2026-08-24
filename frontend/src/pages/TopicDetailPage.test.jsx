import { describe, expect, it, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { Route, Routes } from 'react-router-dom';
import { TopicDetailPage } from './TopicDetailPage';
import { renderWithProviders } from '../test/utils';

vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn(() => ({
    user: { id: 'u1', role: { name: 'citizen' } },
    hasRole: () => false,
  })),
}));

vi.mock('../context/OrganizationContext', () => ({
  useOrganization: vi.fn(() => ({ isOrgModerator: false })),
}));

vi.mock('../lib/services', () => ({
  forumService: {
    getTopic: vi.fn().mockResolvedValue({
      data: {
        id: 't1',
        title: 'What is one peaceful way to check a rumour about an election?',
        content: 'Name an official source before you share.',
        kind: 'question',
        board: 'elections',
        author: 'u1',
        author_name: 'Test Citizen',
        is_approved: true,
        is_locked: false,
        accepted_answer_id: 'c1',
        created_at: '2026-08-02T00:00:00Z',
        comments: [
          {
            id: 'c1',
            author_name: 'Admin User',
            comment: 'Pause and check the National Elections Commission.',
            is_approved: true,
            is_expert: true,
            created_at: '2026-08-02T01:00:00Z',
          },
        ],
      },
    }),
    addComment: vi.fn(),
    reportTopic: vi.fn(),
    reportComment: vi.fn(),
    acceptAnswer: vi.fn(),
    lockTopic: vi.fn(),
  },
}));

describe('TopicDetailPage', () => {
  it('shows expert answers, reporting, and Q&A controls', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/forum/:id" element={<TopicDetailPage />} />
      </Routes>,
      { route: '/forum/t1' },
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /peaceful way to check a rumour/i })).toBeInTheDocument();
    });
    expect(screen.getByText('Expert')).toBeInTheDocument();
    expect(screen.getByText('Accepted answer')).toBeInTheDocument();
    expect(screen.getAllByText('Report').length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByLabelText(/why are you reporting this/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/hate speech/i).length).toBeGreaterThanOrEqual(1);
  });
});
