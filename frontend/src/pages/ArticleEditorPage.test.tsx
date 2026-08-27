import { describe, expect, it, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import { ArticleEditorPage } from './ArticleEditorPage';
import { renderWithProviders } from '../test/utils';

vi.mock('../lib/services', () => ({
  categoryService: {
    list: vi.fn().mockResolvedValue({ data: { results: [{ id: 'c1', name: 'Constitution' }] } }),
  },
  mediaService: {
    list: vi.fn().mockResolvedValue({ data: { results: [] } }),
  },
  articleService: {
    get: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    uploadImage: vi.fn(),
    uploadAttachment: vi.fn(),
  },
}));

describe('ArticleEditorPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders a CMS editor for a new article', async () => {
    renderWithProviders(<ArticleEditorPage />, { route: '/articles/new' });
    expect(await screen.findByRole('heading', { name: /new article/i })).toBeInTheDocument();
    expect(screen.getByText('Publish')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
  });
});
