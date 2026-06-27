import { describe, expect, it, vi } from 'vitest';
import en from '../i18n/en.json';

vi.mock('../lib/services', () => ({
  authService: { sendPhoneVerify: vi.fn(), confirmPhoneVerify: vi.fn() },
  userService: { updateProfile: vi.fn(), uploadAvatar: vi.fn() },
  notificationService: { subscribePush: vi.fn(), unsubscribePush: vi.fn() },
}));

describe('ProfilePage push copy', () => {
  it('includes enable and disable strings for profile settings', () => {
    expect(en.push.profileTitle).toBeTruthy();
    expect(en.push.disable).toMatch(/disable/i);
    expect(en.push.enabled).toBeTruthy();
  });
});
