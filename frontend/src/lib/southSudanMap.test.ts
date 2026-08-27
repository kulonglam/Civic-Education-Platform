import { describe, expect, it } from 'vitest';
import {
  MAP_BOUNDS,
  projectLonLat,
  ringsToPath,
  SOUTH_SUDAN_STATES,
} from './southSudanMap';

const STATE_KEYS = [
  'central_equatoria',
  'eastern_equatoria',
  'western_equatoria',
  'jonglei',
  'unity',
  'upper_nile',
  'lakes',
  'warrap',
  'northern_bahr_el_ghazal',
  'western_bahr_el_ghazal',
];

function pointInRing(lon: number, lat: number, ring: number[][]) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    const intersect =
      yi > lat !== yj > lat && lon < ((xj - xi) * (lat - yi)) / (yj - yi + Number.EPSILON) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}

describe('southSudanMap', () => {
  it('includes the ten restored states used on learner profiles', () => {
    expect(SOUTH_SUDAN_STATES.map((state) => state.key)).toEqual(STATE_KEYS);
  });

  it('uses real GeoJSON outlines, not 8-point boxes', () => {
    for (const state of SOUTH_SUDAN_STATES) {
      const verts = state.rings.reduce((sum, ring) => sum + ring.length, 0);
      expect(verts).toBeGreaterThan(20);
      expect(ringsToPath(state.rings)).toMatch(/^M/);
    }
  });

  it('places Juba inside Central Equatoria and the SVG viewBox', () => {
    const juba: [number, number] = [31.58, 4.85];
    const central = SOUTH_SUDAN_STATES.find((state) => state.key === 'central_equatoria');
    expect(central).toBeDefined();
    expect(pointInRing(juba[0], juba[1], central!.rings[0])).toBe(true);

    const [x, y] = projectLonLat(...juba);
    expect(x).toBeGreaterThan(0);
    expect(y).toBeGreaterThan(0);
    expect(x).toBeLessThan(640);
    expect(y).toBeLessThan(520);
  });

  it('fits the country in the padded bounds', () => {
    expect(MAP_BOUNDS.minLon).toBeLessThan(24.2);
    expect(MAP_BOUNDS.maxLon).toBeGreaterThan(35.9);
    expect(MAP_BOUNDS.minLat).toBeLessThan(3.5);
    expect(MAP_BOUNDS.maxLat).toBeGreaterThan(12.2);
  });
});
