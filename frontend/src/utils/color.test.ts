import { describe, expect, it } from 'vitest';

import { hexToHsv, hsvToHex, isValidHex } from './color';

describe('color conversions', () => {
  it('round-trips known hex values through HSV', () => {
    for (const hex of ['#FF0000', '#00FF00', '#0000FF', '#257BF4', '#1DA597']) {
      expect(hsvToHex(hexToHsv(hex))).toBe(hex);
    }
  });

  it('validates hex strings', () => {
    expect(isValidHex('#112233')).toBe(true);
    expect(isValidHex('#12')).toBe(false);
    expect(isValidHex('112233')).toBe(false);
  });
});
