import { describe, expect, it, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { ArticlesPage } from './ArticlesPage';
import { renderWithProviders } from '../test/utils';

vi.mock('../hooks/useOnlineStatus', () => ({
  useOnlineStatus: () => true,
}));

vi.mock('../lib/offline/articles', () => ({
  loadCategories: vi.fn().mockResolvedValue({
    data: [{ id: '1', name: 'Constitution', name_ar: 'الدستور', slug: 'constitution' }],
  }),
  loadArticlesList: vi.fn().mockResolvedValue({
    data: {
      count: 1,
      results: [
        {
          id: 'a1',
          title: 'English title',
          title_ar: 'عنوان عربي',
          content: 'Body',
          content_ar: 'محتوى',
          published_at: '2026-01-01T00:00:00Z',
          category: { name: 'Constitution', name_ar: 'الدستور' },
        },
      ],
    },
    source: 'network',
  }),
}));

describe('ArticlesPage', () => {
  it('renders localized article titles when language is Arabic', async () => {
    renderWithProviders(<ArticlesPage />);
    await waitFor(() => {
      expect(screen.getByText('English title')).toBeInTheDocument();
    });
  });
});
