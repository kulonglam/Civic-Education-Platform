import { describe, expect, it, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AccessibilityMenu } from './AccessibilityMenu';
import { applyA11ySettings, parseVtt, readA11ySettings } from '../lib/a11y';
import { renderWithProviders } from '../test/utils';

describe('parseVtt', () => {
  it('extracts caption text and skips timestamps', () => {
    const vtt = `WEBVTT

1
00:00:00.000 --> 00:00:02.000
Hello citizens.

2
00:00:02.000 --> 00:00:04.000
This is a civic lesson.
`;
    expect(parseVtt(vtt)).toBe('Hello citizens. This is a civic lesson.');
  });
});

describe('AccessibilityMenu', () => {
  beforeEach(() => {
    document.documentElement.removeAttribute('data-font-size');
    document.documentElement.removeAttribute('data-contrast');
    localStorage.clear();
  });

  it('lets a visitor enlarge text and turn on high contrast', async () => {
    const user = userEvent.setup();
    renderWithProviders(<AccessibilityMenu />);

    await user.click(screen.getByRole('button', { name: /accessibility options/i }));
    expect(screen.getByRole('dialog', { name: /accessibility/i })).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: '150%' }));
    expect(document.documentElement.dataset.fontSize).toBe('xl');
    expect(readA11ySettings().fontScale).toBe('xl');

    await user.click(screen.getByRole('checkbox', { name: /high contrast/i }));
    expect(document.documentElement.dataset.contrast).toBe('high');
    expect(readA11ySettings().highContrast).toBe(true);
    applyA11ySettings(readA11ySettings());
  });
});
