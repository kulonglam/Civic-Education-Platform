/** South Sudan civic photos served from /public/civic. */

export const CIVIC_PHOTOS = {
  independence: '/civic/independence.jpg',
  silhouettes: '/civic/silhouettes.jpg',
  ceremony: '/civic/ceremony.jpg',
  flagRun: '/civic/flag-run.jpg',
  tradition: '/civic/tradition.jpg',
  flagBearer: '/civic/flag-bearer.jpg',
  communityWork: '/civic/community-work.jpg',
  womenFlags: '/civic/women-flags.jpg',
  crowdFlags: '/civic/crowd-flags.jpg',
  officials: '/civic/officials.jpg',
  children: '/civic/children.jpg',
} as const;

export type CivicPhotoKey = keyof typeof CIVIC_PHOTOS;

export const HERO_PHOTO = '/hero-civic.jpg';
export const AUTH_PANEL_PHOTO = CIVIC_PHOTOS.flagBearer;

const TOPIC_PHOTO_SLUGS: Record<string, CivicPhotoKey> = {
  constitution: 'independence',
  'human-rights': 'children',
  'citizen-responsibilities': 'communityWork',
  'government-structure': 'officials',
  governance: 'ceremony',
  elections: 'crowdFlags',
  'rule-of-law': 'ceremony',
  peacebuilding: 'silhouettes',
  'gender-equality': 'womenFlags',
  'anti-corruption': 'officials',
  'public-participation': 'flagBearer',
  'media-misinformation': 'crowdFlags',
  'digital-citizenship': 'children',
  'community-leadership': 'tradition',
  'conflict-resolution': 'silhouettes',
};

export function photoForTopic(slug?: string | null): string {
  if (!slug) return CIVIC_PHOTOS.independence;
  const key = TOPIC_PHOTO_SLUGS[slug];
  return key ? CIVIC_PHOTOS[key] : CIVIC_PHOTOS.independence;
}

export const PAGE_COVERS = {
  news: CIVIC_PHOTOS.crowdFlags,
  events: CIVIC_PHOTOS.flagRun,
  engage: CIVIC_PHOTOS.flagBearer,
  awareness: CIVIC_PHOTOS.communityWork,
  map: CIVIC_PHOTOS.ceremony,
  articles: CIVIC_PHOTOS.independence,
} as const;
