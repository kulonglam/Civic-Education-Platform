import { describe, expect, it } from 'vitest';
import { resolveMediaUrl } from './media';

describe('resolveMediaUrl', () => {
  it('returns absolute URLs unchanged', () => {
    expect(resolveMediaUrl('https://cdn.example.com/doc.pdf')).toBe('https://cdn.example.com/doc.pdf');
  });

  it('prefixes relative media paths with API origin', () => {
    expect(resolveMediaUrl('/media/articles/x.pdf')).toBe('http://127.0.0.1:8000/media/articles/x.pdf');
  });

  it('returns empty string for falsy input', () => {
    expect(resolveMediaUrl('')).toBe('');
  });
});
