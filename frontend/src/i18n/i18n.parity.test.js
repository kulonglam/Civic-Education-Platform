import { describe, expect, it } from 'vitest';
import ar from './ar.json';
import en from './en.json';

function leafKeys(value, prefix = '') {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return Object.entries(value).flatMap(([key, child]) =>
      leafKeys(child, prefix ? `${prefix}.${key}` : key),
    );
  }
  if (Array.isArray(value)) {
    return value.flatMap((item, index) => leafKeys(item, `${prefix}[${index}]`));
  }
  return [prefix];
}

describe('i18n completeness', () => {
  it('keeps Arabic keys in lockstep with English', () => {
    const english = leafKeys(en);
    const arabic = new Set(leafKeys(ar));
    expect(english.filter((key) => !arabic.has(key))).toEqual([]);
  });
});
