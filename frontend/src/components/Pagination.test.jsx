import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Pagination } from './Pagination';

describe('Pagination', () => {
  it('renders controls and calls onPageChange', async () => {
    const onPageChange = vi.fn();
    render(
      <Pagination page={2} totalCount={45} pageSize={20} onPageChange={onPageChange} />
    );
    expect(screen.getByText(/page 2 of 3/i)).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /next/i }));
    expect(onPageChange).toHaveBeenCalledWith(3);
  });

  it('hides when only one page', () => {
    const { container } = render(
      <Pagination page={1} totalCount={5} pageSize={20} onPageChange={() => {}} />
    );
    expect(container).toBeEmptyDOMElement();
  });
});
