import { describe, expect, it } from 'vitest';
import { isWakeFailure } from './apiHealth';

describe('apiHealth', () => {
  it('treats network failures and gateway timeouts as a waking API', () => {
    expect(isWakeFailure({ message: 'Network Error' })).toBe(true);
    expect(isWakeFailure({ response: { status: 502 } })).toBe(true);
    expect(isWakeFailure({ response: { status: 504 } })).toBe(true);
  });

  it('does not treat tutor 503 or auth errors as a cold start', () => {
    expect(isWakeFailure({ response: { status: 503 } })).toBe(false);
    expect(isWakeFailure({ response: { status: 401 } })).toBe(false);
    expect(isWakeFailure({ response: { status: 404 } })).toBe(false);
  });
});
