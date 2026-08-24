import { describe, expect, it } from 'vitest';
import { pickVoice } from './speech';

describe('pickVoice', () => {
  it('prefers an Arabic voice for Arabic read-aloud', () => {
    const voices = [
      { lang: 'en-US', name: 'English' },
      { lang: 'ar-EG', name: 'Arabic Egypt' },
      { lang: 'ar-SA', name: 'Arabic Saudi' },
    ];
    expect(pickVoice('ar', voices)?.name).toBe('Arabic Egypt');
  });

  it('falls back to any ar-* voice', () => {
    const voices = [
      { lang: 'en-GB', name: 'English' },
      { lang: 'ar-SA', name: 'Arabic Saudi' },
    ];
    expect(pickVoice('ar', voices)?.name).toBe('Arabic Saudi');
  });

  it('prefers en-US for English', () => {
    const voices = [
      { lang: 'en-GB', name: 'British' },
      { lang: 'en-US', name: 'US English' },
    ];
    expect(pickVoice('en', voices)?.name).toBe('US English');
  });
});
