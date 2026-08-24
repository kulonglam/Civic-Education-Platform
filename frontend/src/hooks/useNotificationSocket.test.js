import { describe, expect, it } from 'vitest';
import { notificationSocketUrl } from './useNotificationSocket';

describe('notificationSocketUrl', () => {
  it('strips the API prefix and appends the access token', () => {
    expect(notificationSocketUrl('abc.def')).toMatch(/\/ws\/notifications\/\?token=abc\.def$/);
  });
});
