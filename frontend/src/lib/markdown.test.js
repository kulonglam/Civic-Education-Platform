import { describe, expect, it } from 'vitest';
import { plainTextExcerpt } from './markdown';

describe('plainTextExcerpt', () => {
  it('strips markdown syntax for card previews', () => {
    const text = '## Heading\n\n**Bold** and [link](https://example.com) text.';
    expect(plainTextExcerpt(text)).toBe('Heading Bold and link text.');
  });

  it('truncates long text with ellipsis', () => {
    const text = 'word '.repeat(50);
    const excerpt = plainTextExcerpt(text, 20);
    expect(excerpt.length).toBeLessThanOrEqual(21);
    expect(excerpt.endsWith('…')).toBe(true);
  });
});
