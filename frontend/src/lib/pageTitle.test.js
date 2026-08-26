import { describe, expect, it } from 'vitest';
import { documentTitle, titleKeyForPath } from './pageTitle';

const t = (key) =>
  ({
    'app.name': 'Civic Education RSS',
    'app.tagline': 'Building informed citizens',
    'nav.articles': 'Articles',
    'nav.manageArticles': 'Manage articles',
    'nav.login': 'Log in',
    'errors.notFoundTitle': 'Page not found',
  })[key] ?? key;

describe('page titles', () => {
  it('uses the product name and tagline on home', () => {
    expect(titleKeyForPath('/')).toBe('nav.home');
    expect(documentTitle('/', t)).toBe('Civic Education RSS — Building informed citizens');
  });

  it('prefers the more specific manage route over the public list', () => {
    expect(titleKeyForPath('/articles/manage')).toBe('nav.manageArticles');
    expect(documentTitle('/articles/manage', t)).toBe('Manage articles · Civic Education RSS');
  });

  it('titles auth screens', () => {
    expect(titleKeyForPath('/login')).toBe('nav.login');
    expect(documentTitle('/login', t)).toBe('Log in · Civic Education RSS');
  });
});
