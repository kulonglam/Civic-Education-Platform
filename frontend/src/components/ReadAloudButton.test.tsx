import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ReadAloudButton } from './ReadAloudButton';
import { renderWithProviders } from '../test/utils';

describe('ReadAloudButton', () => {
  const speak = vi.fn();
  const cancel = vi.fn();

  beforeEach(() => {
    speak.mockClear();
    cancel.mockClear();
    vi.stubGlobal('speechSynthesis', { speak, cancel, getVoices: () => [] });
    vi.stubGlobal(
      'SpeechSynthesisUtterance',
      class {
        text: string;
        constructor(text: string) {
          this.text = text;
        }
      },
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('reads the provided text aloud', async () => {
    const user = userEvent.setup();
    renderWithProviders(<ReadAloudButton text="The constitution is the supreme law." />);

    await user.click(screen.getByRole('button', { name: /listen/i }));
    expect(cancel).toHaveBeenCalled();
    expect(speak).toHaveBeenCalled();
    expect(speak.mock.calls[0][0].text).toMatch(/constitution is the supreme law/i);
  });
});
