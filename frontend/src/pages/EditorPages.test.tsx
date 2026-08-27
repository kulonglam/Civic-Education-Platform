import { describe, expect, it, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import { QuizEditorPage } from './QuizEditorPage';
import { CourseEditorPage } from './CourseEditorPage';
import { MediaEditorPage } from './MediaEditorPage';
import { renderWithProviders } from '../test/utils';

vi.mock('../lib/services', () => ({
  quizService: {
    get: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
  },
  articleService: {
    list: vi.fn().mockResolvedValue({
      data: { results: [{ id: 'a1', title: 'Bill of Rights' }] },
    }),
  },
  courseService: {
    get: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
  },
  categoryService: {
    list: vi.fn().mockResolvedValue({
      data: { results: [{ id: 'c1', name: 'Constitution' }] },
    }),
  },
  mediaService: {
    get: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
  },
}));

describe('CMS editors', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the quiz editor on the CMS layout', async () => {
    renderWithProviders(<QuizEditorPage />, { route: '/quizzes/new' });
    expect(await screen.findByRole('heading', { name: /new quiz/i })).toBeInTheDocument();
    expect(screen.getByText('Publish')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
  });

  it('renders the course editor on the CMS layout', async () => {
    renderWithProviders(<CourseEditorPage />, { route: '/courses/new' });
    expect(await screen.findByRole('heading', { name: /new course/i })).toBeInTheDocument();
    expect(screen.getByText('Publish')).toBeInTheDocument();
    expect(await screen.findByText('Bill of Rights')).toBeInTheDocument();
  });

  it('renders the media editor on the CMS layout', async () => {
    renderWithProviders(<MediaEditorPage />, { route: '/media/new' });
    expect(await screen.findByRole('heading', { name: /new media/i })).toBeInTheDocument();
    expect(screen.getByText('Publish')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
  });
});
