import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { StatusBadge, CmsManageHeader } from './CmsWorkspace';

describe('CmsWorkspace', () => {
  it('renders a published status badge', () => {
    render(<StatusBadge status="published" label="Published" />);
    expect(screen.getByText('Published')).toBeInTheDocument();
  });

  it('shows the content workspace eyebrow', () => {
    render(
      <MemoryRouter>
        <CmsManageHeader title="Manage articles" subtitle="Edit lessons" primaryTo="/articles/new" primaryLabel="Create" />
      </MemoryRouter>,
    );
    expect(screen.getByText(/content workspace/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Create' })).toHaveAttribute('href', '/articles/new');
  });
});
