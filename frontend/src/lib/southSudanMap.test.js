import { describe, expect, it } from 'vitest';
import { projectLonLat, ringToPath, SOUTH_SUDAN_STATES } from './southSudanMap';

describe('southSudanMap', () => {
  it('includes the ten states used on learner profiles', () => {
    expect(SOUTH_SUDAN_STATES.map((state) => state.key)).toEqual(
      expect.arrayContaining(['central_equatoria', 'jonglei', 'upper_nile']),
    );
    expect(SOUTH_SUDAN_STATES).toHaveLength(10);
  });

  it('projects Juba-ish coordinates inside the SVG viewBox', () => {
    const [x, y] = projectLonLat(31.58, 4.85);
    expect(x).toBeGreaterThan(0);
    expect(y).toBeGreaterThan(0);
    expect(ringToPath(SOUTH_SUDAN_STATES[0].ring)).toMatch(/^M/);
  });
});
