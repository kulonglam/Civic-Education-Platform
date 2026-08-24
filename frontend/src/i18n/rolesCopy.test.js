import { describe, expect, it } from 'vitest';
import en from '../i18n/en.json';

describe('role and org admin copy', () => {
  it('explains recommended platform roles', () => {
    expect(en.roles.modelTitle).toMatch(/recommended user roles/i);
    expect(en.roles.perm_guest).toMatch(/browse public/i);
    expect(en.roles.perm_citizen).toMatch(/learn/i);
    expect(en.roles.perm_editor).toMatch(/educational content/i);
    expect(en.roles.perm_moderator).toMatch(/discussions/i);
    expect(en.roles.perm_admin).toMatch(/full operational control/i);
    expect(en.roles.perm_super_admin).toMatch(/configuration and security/i);
  });

  it('documents admin panel guidance', () => {
    expect(en.admin.platformRolesHint).toMatch(/super admins/i);
    expect(en.admin.moderationPanelDesc).toMatch(/moderation queue/i);
  });
});
