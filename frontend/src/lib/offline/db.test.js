import { describe, expect, it, vi } from 'vitest';

vi.mock('../api', () => ({
  tenantStore: { slug: 'demo-org' },
}));

describe('offline db scopeKey', () => {
  it('scopes cache keys to the current organization', async () => {
    const { scopeKey } = await import('./db');
    expect(scopeKey('article-1')).toBe('demo-org:article-1');
  });
});
