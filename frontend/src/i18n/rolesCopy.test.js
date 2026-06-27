import { describe, expect, it } from 'vitest';
import en from '../i18n/en.json';

describe('role and org admin copy', () => {
  it('explains platform vs organization roles', () => {
    expect(en.roles.platformRoleDesc).toMatch(/platform admin/i);
    expect(en.roles.orgAdminPanelDesc).toMatch(/platform admins only/i);
  });

  it('documents admin panel guidance', () => {
    expect(en.admin.platformRolesHint).toMatch(/platform admins/i);
    expect(en.admin.moderationPanelDesc).toMatch(/moderation queue/i);
  });
});
