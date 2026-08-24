import { describe, expect, it, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { AwarenessPage } from './AwarenessPage';
import { renderWithProviders } from '../test/utils';

vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn(() => ({ user: null, hasRole: () => false })),
}));

vi.mock('../lib/services', () => ({
  awarenessService: {
    overview: vi.fn().mockResolvedValue({
      data: {
        quiz: { id: 'q-ff', title: 'Fact or Fiction?' },
        lessons: [
          { key: 'verify', article_id: 'a1', title: 'Pause before you share' },
          { key: 'examples', article_id: 'a2', title: 'Teaching examples' },
          { key: 'social', article_id: 'a3', title: 'Social media' },
          { key: 'credibility', article_id: 'a4', title: 'Source credibility' },
        ],
      },
    }),
    report: vi.fn(),
  },
}));

describe('AwarenessPage', () => {
  it('shows the six awareness tracks and a report form', async () => {
    renderWithProviders(<AwarenessPage />);

    expect(screen.getByRole('heading', { name: /misinformation awareness/i })).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByRole('link', { name: /fact or fiction/i })).toHaveAttribute(
        'href',
        '/quizzes/q-ff',
      );
    });
    expect(screen.getByRole('link', { name: /how to verify/i })).toHaveAttribute('href', '/articles/a1');
    expect(screen.getByRole('link', { name: /fake news examples/i })).toHaveAttribute('href', '/articles/a2');
    expect(screen.getByRole('link', { name: /social media rumours/i })).toHaveAttribute('href', '/articles/a3');
    expect(screen.getByRole('link', { name: /source credibility/i })).toHaveAttribute('href', '/articles/a4');
    expect(screen.getAllByRole('heading', { name: /report suspicious content/i }).length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText(/do not paste the full rumour/i).length).toBeGreaterThanOrEqual(1);
  });
});
