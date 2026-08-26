import { describe, expect, it, vi } from 'vitest';
import { screen } from '@testing-library/react';
import { ErrorBoundary } from './ErrorBoundary';
import { renderWithProviders } from '../test/utils';

vi.spyOn(console, 'error').mockImplementation(() => {});

function Boom() {
  throw new Error('boom');
}

describe('ErrorBoundary', () => {
  it('offers a way home when a screen crashes', () => {
    renderWithProviders(
      <ErrorBoundary>
        <Boom />
      </ErrorBoundary>,
    );
    expect(screen.getByRole('heading', { name: /something went wrong/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /go back home/i })).toHaveAttribute('href', '/');
    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
  });
});
