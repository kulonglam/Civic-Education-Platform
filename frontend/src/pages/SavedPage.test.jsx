import { describe, expect, it, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { SavedPage } from '../pages/SavedPage';
import { renderWithProviders } from '../test/utils';

vi.mock('../lib/services', () => ({
  bookmarkService: {
    list: vi.fn().mockResolvedValue({
      data: {
        count: 1,
        results: [
          {
            id: 'b1',
            kind: 'article',
            article: {
              id: 'a1',
              title: 'Civic Rights',
              category_name: 'Constitution',
              published_at: '2026-01-01T00:00:00Z',
            },
            media: null,
          },
        ],
      },
    }),
    remove: vi.fn(),
  },
}));

describe('SavedPage', () => {
  it('renders bookmarked lessons', async () => {
    renderWithProviders(<SavedPage />);
    await waitFor(() => {
      expect(screen.getByRole('link', { name: /civic rights/i })).toHaveAttribute(
        'href',
        '/articles/a1',
      );
    });
    expect(screen.getByText(/constitution/i)).toBeInTheDocument();
  });
});
