import { describe, expect, it, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import { ArticlesManagePage } from './ArticlesManagePage';
import { renderWithProviders } from '../test/utils';

const mockHasRole = vi.fn();
const list = vi.fn();
const remove = vi.fn();
const approve = vi.fn();
const reject = vi.fn();

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({ hasRole: (...roles) => mockHasRole(...roles) }),
}));

vi.mock('../context/OrganizationContext', () => ({
  useOrganization: () => ({ membership: { role: 'owner' }, isOrgAdmin: true }),
}));

vi.mock('../lib/services', () => ({
  articleService: {
    list: (...args) => list(...args),
    remove: (...args) => remove(...args),
    approve: (...args) => approve(...args),
    reject: (...args) => reject(...args),
  },
}));

describe('ArticlesManagePage', () => {
  beforeEach(() => {
    mockHasRole.mockReturnValue(true);
    list.mockResolvedValue({
      data: {
        results: [
          {
            id: 'a1',
            title: 'Transitional Constitution',
            status: 'draft',
            updated_at: '2026-08-01T00:00:00Z',
            category: { name: 'Constitution' },
          },
        ],
      },
    });
  });

  it('lists articles in the content workspace', async () => {
    renderWithProviders(<ArticlesManagePage />);
    expect(await screen.findByRole('heading', { name: /manage articles/i })).toBeInTheDocument();
    expect(screen.getByText(/content workspace/i)).toBeInTheDocument();
    expect(screen.getByText('Transitional Constitution')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /new article/i })).toHaveAttribute('href', '/articles/new');
    expect(screen.getByRole('link', { name: /^edit$/i })).toHaveAttribute('href', '/articles/a1/edit');
  });
});
