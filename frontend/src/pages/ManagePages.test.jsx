import { describe, expect, it, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import { NewsManagePage } from './NewsManagePage';
import { EventsManagePage } from './EventsManagePage';
import { MediaManagePage } from './MediaManagePage';
import { QuizzesManagePage } from './QuizzesManagePage';
import { CoursesManagePage } from './CoursesManagePage';
import { CategoriesManagePage } from './CategoriesManagePage';
import { EngagementManagePage } from './EngagementManagePage';
import { renderWithProviders } from '../test/utils';

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({ hasRole: () => true }),
}));

vi.mock('../context/OrganizationContext', () => ({
  useOrganization: () => ({ isOrgAdmin: true }),
}));

vi.mock('../lib/services', () => ({
  newsService: {
    list: vi.fn().mockResolvedValue({
      data: { results: [{ id: 'n1', title: 'Election notice', topic: 'election', claim_type: 'official', status: 'published' }] },
    }),
    remove: vi.fn(),
  },
  eventsService: {
    list: vi.fn().mockResolvedValue({
      data: { results: [{ id: 'e1', title: 'Civic workshop', kind: 'workshop', starts_at: '2026-09-01T09:00:00Z', status: 'draft' }] },
    }),
    remove: vi.fn(),
  },
  mediaService: {
    list: vi.fn().mockResolvedValue({
      data: { results: [{ id: 'm1', title: 'Radio lesson', media_type: 'audio', status: 'published', published_at: '2026-08-01T00:00:00Z' }] },
    }),
    remove: vi.fn(),
  },
  quizService: {
    list: vi.fn().mockResolvedValue({
      data: { results: [{ id: 'q1', title: 'Rights quiz', passing_score: 70, question_count: 5, is_active: true }] },
    }),
    remove: vi.fn(),
  },
  courseService: {
    list: vi.fn().mockResolvedValue({
      data: { results: [{ id: 'c1', title: 'Civic path', lesson_count: 3, status: 'draft' }] },
    }),
    remove: vi.fn(),
  },
  categoryService: {
    list: vi.fn().mockResolvedValue({
      data: { results: [{ id: 'cat1', name: 'Constitution', slug: 'constitution', is_locked: false }] },
    }),
    remove: vi.fn(),
  },
  engagementService: {
    polls: vi.fn().mockResolvedValue({
      data: { results: [{ id: 'p1', question: 'Should civic class be weekly?', status: 'draft' }] },
    }),
    petitions: vi.fn().mockResolvedValue({ data: { results: [] } }),
    campaigns: vi.fn().mockResolvedValue({ data: { results: [] } }),
    removePoll: vi.fn(),
    removePetition: vi.fn(),
    removeCampaign: vi.fn(),
  },
}));

describe('manage pages', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows news workspace rows', async () => {
    renderWithProviders(<NewsManagePage />);
    expect(await screen.findByText('Election notice')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /new civic notice/i })).toHaveAttribute('href', '/news/new');
  });

  it('shows events workspace rows', async () => {
    renderWithProviders(<EventsManagePage />);
    expect(await screen.findByText('Civic workshop')).toBeInTheDocument();
  });

  it('shows media workspace rows', async () => {
    renderWithProviders(<MediaManagePage />);
    expect(await screen.findByText('Radio lesson')).toBeInTheDocument();
  });

  it('shows quizzes workspace rows', async () => {
    renderWithProviders(<QuizzesManagePage />);
    expect(await screen.findByText('Rights quiz')).toBeInTheDocument();
  });

  it('shows courses workspace rows', async () => {
    renderWithProviders(<CoursesManagePage />);
    expect(await screen.findByText('Civic path')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /new course/i })).toHaveAttribute('href', '/courses/new');
  });

  it('shows categories workspace rows', async () => {
    renderWithProviders(<CategoriesManagePage />);
    expect(await screen.findByText('Constitution')).toBeInTheDocument();
  });

  it('shows engagement workspace rows', async () => {
    renderWithProviders(<EngagementManagePage />);
    expect(await screen.findByText('Should civic class be weekly?')).toBeInTheDocument();
  });
});
