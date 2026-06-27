import { describe, expect, it, vi } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QuizTakePage } from './QuizTakePage';
import { renderWithProviders } from '../test/utils';

const mockQuiz = {
  id: 'quiz-1',
  title: 'Civic Basics',
  description: 'Test your knowledge',
  questions: [
    {
      id: 'q1',
      question_text: 'Question one?',
      question_type: 'mcq',
      options: ['A', 'B'],
    },
    {
      id: 'q2',
      question_text: 'Question two?',
      question_type: 'true_false',
      options: [],
    },
  ],
};

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return { ...actual, useParams: () => ({ id: 'quiz-1' }) };
});

vi.mock('../hooks/useOnlineStatus', () => ({
  useOnlineStatus: () => true,
}));

vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQuery: () => ({
      data: { data: mockQuiz, source: 'network' },
      isLoading: false,
    }),
    useMutation: () => ({ mutate: vi.fn(), isPending: false }),
  };
});

describe('QuizTakePage', () => {
  it('renders quiz questions and disables submit until all answered', async () => {
    renderWithProviders(<QuizTakePage />);
    expect(screen.getByText('Civic Basics')).toBeInTheDocument();
    expect(screen.getByText(/question one/i)).toBeInTheDocument();

    const submit = screen.getByRole('button', { name: /submit answers/i });
    expect(submit).toBeDisabled();

    await userEvent.click(screen.getByLabelText('A'));
    expect(submit).toBeDisabled();

    await userEvent.click(screen.getByLabelText('True'));
    expect(submit).not.toBeDisabled();
  });
});
