import { describe, expect, it } from 'vitest';
import { whatsappClickToChatUrl, whatsappShareUrl } from './whatsapp';

describe('whatsappShareUrl', () => {
  it('encodes title and page URL for wa.me', () => {
    const href = whatsappShareUrl('Civic lesson', 'https://example.test/articles/1');
    expect(href.startsWith('https://wa.me/?text=')).toBe(true);
    expect(decodeURIComponent(href)).toContain('Civic lesson');
    expect(decodeURIComponent(href)).toContain('https://example.test/articles/1');
  });
});

describe('whatsappClickToChatUrl', () => {
  it('strips plus and spaces from a display number', () => {
    expect(whatsappClickToChatUrl('+211 922 000 000')).toBe('https://wa.me/211922000000');
  });
});
