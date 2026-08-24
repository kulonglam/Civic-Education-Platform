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

  it('shows a check-answer control when feedback is per question', () => {
    mockQuiz.feedback_mode = 'per_question';
    mockQuiz.kind = 'practice';
    renderWithProviders(<QuizTakePage />);
    expect(screen.getAllByRole('button', { name: /check answer/i })).toHaveLength(2);
    mockQuiz.feedback_mode = 'end';
    mockQuiz.kind = 'assessment';
  });

  it('renders a scenario as a civic situation', () => {
    const previous = mockQuiz.questions;
    mockQuiz.questions = [
      {
        id: 's1',
        question_text: 'You witness corruption in a public institution. What are your legal and civic options?',
        question_type: 'scenario',
        options: ['Report through official channels', 'Stay silent'],
      },
    ];
    renderWithProviders(<QuizTakePage />);
    expect(screen.getByText(/situation/i)).toBeInTheDocument();
    expect(screen.getByText(/witness corruption/i)).toBeInTheDocument();
    mockQuiz.questions = previous;
  });
});
