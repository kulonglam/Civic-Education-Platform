/** Simplified South Sudan 10-state rings [lon, lat] for the civic map. */

export const MAP_BOUNDS = {
  minLon: 23.4,
  maxLon: 36.1,
  minLat: 3.4,
  maxLat: 12.3,
};

export const SOUTH_SUDAN_STATES = [
  {
    key: 'northern_bahr_el_ghazal',
    ring: [
      [25.0, 10.2], [28.5, 10.2], [28.3, 9.0], [27.5, 9.0], [25.8, 8.8], [24.5, 9.4], [25.0, 10.2],
    ],
  },
  {
    key: 'western_bahr_el_ghazal',
    ring: [
      [24.2, 9.4], [25.8, 8.8], [27.2, 7.5], [27.4, 6.2], [26.8, 5.5], [24.2, 7.2], [23.6, 8.6], [24.2, 9.4],
    ],
  },
  {
    key: 'warrap',
    ring: [
      [27.5, 9.0], [29.2, 8.4], [30.4, 7.6], [28.8, 7.6], [28.2, 6.8], [27.2, 7.5], [27.5, 9.0],
    ],
  },
  {
    key: 'unity',
    ring: [
      [28.5, 10.2], [31.0, 10.4], [31.5, 9.0], [30.8, 8.5], [29.2, 8.4], [28.3, 9.0], [28.5, 10.2],
    ],
  },
  {
    key: 'upper_nile',
    ring: [
      [31.0, 12.1], [34.0, 12.0], [34.2, 9.5], [33.8, 8.0], [32.2, 9.2], [31.5, 9.0], [31.0, 10.4], [31.0, 12.1],
    ],
  },
  {
    key: 'jonglei',
    ring: [
      [30.8, 8.5], [32.2, 9.2], [33.8, 8.0], [33.5, 6.2], [32.2, 5.9], [31.8, 5.8], [30.5, 5.8], [30.4, 7.0], [30.8, 8.5],
    ],
  },
  {
    key: 'lakes',
    ring: [
      [28.8, 7.6], [30.4, 7.6], [30.4, 6.0], [28.6, 5.9], [28.2, 6.8], [28.8, 7.6],
    ],
  },
  {
    key: 'western_equatoria',
    ring: [
      [27.4, 6.2], [30.2, 6.0], [30.2, 4.2], [29.4, 3.5], [27.7, 4.3], [26.8, 5.5], [27.4, 6.2],
    ],
  },
  {
    key: 'central_equatoria',
    ring: [
      [30.5, 5.8], [31.8, 5.8], [32.4, 4.9], [32.2, 3.6], [31.0, 3.5], [30.2, 4.2], [30.5, 5.8],
    ],
  },
  {
    key: 'eastern_equatoria',
    ring: [
      [32.2, 5.9], [33.5, 6.2], [35.9, 5.0], [35.0, 3.5], [32.4, 3.6], [32.2, 4.9], [32.2, 5.9],
    ],
  },
];

const WIDTH = 640;
const HEIGHT = 520;

export function projectLonLat(lon, lat, width = WIDTH, height = HEIGHT) {
  const { minLon, maxLon, minLat, maxLat } = MAP_BOUNDS;
  const x = ((lon - minLon) / (maxLon - minLon)) * width;
  const y = (1 - (lat - minLat) / (maxLat - minLat)) * height;
  return [x, y];
}

export function ringToPath(ring, width = WIDTH, height = HEIGHT) {
  return ring
    .map((point, index) => {
      const [x, y] = projectLonLat(point[0], point[1], width, height);
      return `${index === 0 ? 'M' : 'L'}${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(' ') + ' Z';
}

export const MAP_SIZE = { width: WIDTH, height: HEIGHT };
