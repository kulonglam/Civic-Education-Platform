export function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const payload = token.split('.')[1];
    if (!payload) return null;
    return JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/'))) as Record<string, unknown>;
  } catch {
    return null;
  }
}

export function getOrgSlugFromToken(token?: string | null): string | null {
  if (!token) return null;
  const payload = decodeJwtPayload(token);
  const slug = payload?.org_slug;
  return typeof slug === 'string' && slug ? slug : null;
}
