import { describe, expect, it } from 'vitest';
import { getEmbedInfo } from './mediaEmbed';

describe('getEmbedInfo', () => {
  it('detects YouTube watch URLs', () => {
    expect(getEmbedInfo('https://www.youtube.com/watch?v=0PAy1zBtT9w')).toEqual({
      provider: 'youtube',
      src: 'https://www.youtube.com/embed/0PAy1zBtT9w?cc_load_policy=1&cc_lang_pref=en',
    });
  });

  it('detects youtu.be short links', () => {
    expect(getEmbedInfo('https://youtu.be/0PAy1zBtT9w')).toEqual({
      provider: 'youtube',
      src: 'https://www.youtube.com/embed/0PAy1zBtT9w?cc_load_policy=1&cc_lang_pref=en',
    });
  });

  it('detects Vimeo URLs', () => {
    expect(getEmbedInfo('https://vimeo.com/123456789')).toEqual({
      provider: 'vimeo',
      src: 'https://player.vimeo.com/video/123456789?texttrack=en',
    });
  });

  it('returns null for direct media files', () => {
    expect(getEmbedInfo('https://cdn.example.com/clip.mp4')).toBeNull();
    expect(getEmbedInfo('/media/org/video/x.mp4')).toBeNull();
  });

  it('requests Arabic captions on YouTube embeds', () => {
    expect(getEmbedInfo('https://www.youtube.com/watch?v=0PAy1zBtT9w', { lang: 'ar' })).toEqual({
      provider: 'youtube',
      src: 'https://www.youtube.com/embed/0PAy1zBtT9w?cc_load_policy=1&cc_lang_pref=ar',
    });
  });
});
