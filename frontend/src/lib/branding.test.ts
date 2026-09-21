import { describe, expect, it } from 'vitest';
import { displayOrganizationName, PLATFORM_NAME } from './branding';

describe('displayOrganizationName', () => {
  it('maps the former product title to CivicHub', () => {
    expect(displayOrganizationName('Civic Education RSS')).toBe('CivicHub');
    expect(displayOrganizationName('Civic RSS')).toBe(PLATFORM_NAME);
    expect(displayOrganizationName('التعليم المدني RSS', 'CivicHub')).toBe('CivicHub');
  });

  it('keeps a real tenant name', () => {
    expect(displayOrganizationName('Juba Civic Club')).toBe('Juba Civic Club');
  });

  it('falls back when empty', () => {
    expect(displayOrganizationName(null)).toBe('CivicHub');
    expect(displayOrganizationName(undefined, 'CivicHub')).toBe('CivicHub');
  });
});
