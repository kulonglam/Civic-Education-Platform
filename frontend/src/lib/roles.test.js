import { describe, expect, it } from 'vitest';
import { isPlatformAdminRole, isSuperAdminRole, platformRoleAllowed } from './roles';

describe('platformRoleAllowed', () => {
  it('lets Super Admin through routes that allow Administrator', () => {
    expect(platformRoleAllowed('super_admin', ['admin'])).toBe(true);
    expect(platformRoleAllowed('super_admin', ['admin', 'editor'])).toBe(true);
  });

  it('does not treat Content Creator as Administrator', () => {
    expect(platformRoleAllowed('editor', ['admin'])).toBe(false);
    expect(platformRoleAllowed('citizen', ['admin', 'moderator'])).toBe(false);
  });

  it('detects admin tiers', () => {
    expect(isPlatformAdminRole('admin')).toBe(true);
    expect(isPlatformAdminRole('super_admin')).toBe(true);
    expect(isPlatformAdminRole('editor')).toBe(false);
    expect(isSuperAdminRole('super_admin')).toBe(true);
    expect(isSuperAdminRole('admin')).toBe(false);
  });
});
