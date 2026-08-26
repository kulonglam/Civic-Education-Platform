export const CITIZEN = 'citizen';
export const EDITOR = 'editor';
export const MODERATOR = 'moderator';
export const ADMIN = 'admin';
export const SUPER_ADMIN = 'super_admin';

export function platformRoleAllowed(roleName?: string | null, allowed: string[] = []): boolean {
  if (!roleName || !allowed.length) return false;
  if (allowed.includes(roleName)) return true;
  return roleName === SUPER_ADMIN && allowed.includes(ADMIN);
}

export function isPlatformAdminRole(roleName?: string | null): boolean {
  return roleName === ADMIN || roleName === SUPER_ADMIN;
}

export function isSuperAdminRole(roleName?: string | null): boolean {
  return roleName === SUPER_ADMIN;
}

export const RECOMMENDED_ROLES = [
  { key: 'guest', permKey: 'perm_guest' },
  { key: 'citizen', permKey: 'perm_citizen' },
  { key: 'editor', permKey: 'perm_editor' },
  { key: 'moderator', permKey: 'perm_moderator' },
  { key: 'admin', permKey: 'perm_admin' },
  { key: 'super_admin', permKey: 'perm_super_admin' },
] as const;
