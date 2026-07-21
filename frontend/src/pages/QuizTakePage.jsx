import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { Alert, Spinner } from '../components/ui';
import { AcademicCap, ChevronLeft, CloudArrowDown, Trophy } from '../components/Icons';
import { useOnlineStatus } from '../hooks/useOnlineStatus';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { loadQuiz, queueQuizAttempt } from '../lib/offline/quizzes';
import { localizedQuiz } from '../lib/localizedContent';
import { quizService } from '../lib/services';

function ScoreRing({ score, passed }) {
  const radius = 48;
  const stroke = 8;
  const normalizedRadius = radius - stroke / 2;
  const circumference = 2 * Math.PI * normalizedRadius;
  const offset = circumference - (score / 100) * circumference;
  const color = passed ? '#059669' : '#f59e0b';

  return (
    <div className="relative mx-auto flex h-36 w-36 items-center justify-center">
      <svg className="-rotate-90 h-full w-full" viewBox={`0 0 ${radius * 2} ${radius * 2}`}>
        <circle
          cx={radius}
          cy={radius}
          r={normalizedRadius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={stroke}
          className="dark:stroke-slate-700"
        />
        <circle
          cx={radius}
          cy={radius}
          r={normalizedRadius}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.9s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-extrabold text-gray-900 dark:text-slate-100">{score}%</span>
      </div>
    </div>
  );
}

function QuizProgress({ current, total, answeredCount }) {
  const pct = total > 0 ? Math.round((answeredCount / total) * 100) : 0;
  return (
    <div className="mb-6">
      <div className="mb-1.5 flex items-center justify-between text-sm text-ink-700/60 dark:text-slate-400">
        <span>Question {current + 1} of {total}</span>
        <span>{pct}% answered</span>
      </div>
      <div className="quiz-progress">
        <div className="quiz-progress-bar" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export function QuizTakePage() {
  const { t, i18n } = useTranslation();
  const online = useOnlineStatus();
  const { id } = useParams();
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [queued, setQueued] = useState(false);
  const [error, setError] = useState('');
  const [currentQIdx, setCurrentQIdx] = useState(0);

  const { data: quizResult, isLoading } = useQuery({
    queryKey: queryKeys.quiz(id),
    enabled: !!id,
    queryFn: async () => loadQuiz(id),
  });

  const quiz = localizedQuiz(quizResult?.data, i18n.language);
  const fromCache = quizResult?.source === 'cache';

  const submitAttempt = useMutation({
    mutationFn: async () => {
      if (!online) {
        await queueQuizAttempt(id, answers);
        return { queued: true };
      }
      const { data } = await quizService.attempt(id, answers);
      return { queued: false, data };
    },
    onSuccess: (payload) => {
      if (payload.queued) {
        setQueued(true);
        setResult(null);
      } else {
        setQueued(false);
        setResult(payload.data);
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    onError: (err) => setError(extractError(err)),
  });

  const setAnswer = (questionId, value) =>
    setAnswers((a) => ({ ...a, [questionId]: value }));

  if (isLoading) return <Spinner />;
  if (!quiz) return <Alert>{error || t('common.noResults')}</Alert>;

  if (queued) {
    return (
      <div className="mx-auto max-w-2xl">
        <div className="quiz-stage text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-400">
            <CloudArrowDown className="h-8 w-8" />
          </div>
          <h1 className="mt-4 font-display text-2xl font-semibold dark:text-slate-100">{t('offline.quizQueuedTitle')}</h1>
          <p className="mt-2 text-ink-700/70 dark:text-slate-400">{t('offline.quizQueuedBody')}</p>
          <Link to="/quizzes" className="btn-primary mt-6 inline-block">
            {t('quizzes.title')}
          </Link>
        </div>
      </div>
    );
  }

  if (result) {
    const { attempt, certificate } = result;
    return (
      <div className="mx-auto max-w-lg">
        <div className={`quiz-stage text-center ${attempt.passed ? 'ring-1 ring-emerald-300/80' : 'ring-1 ring-amber-300/80'}`}>
          <div className={`mx-auto mb-2 flex h-14 w-14 items-center justify-center rounded-2xl ${attempt.passed ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-amber-50 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400'}`}>
            {attempt.passed ? <Trophy className="h-7 w-7" /> : <AcademicCap className="h-7 w-7" />}
          </div>

          <ScoreRing score={attempt.score} passed={attempt.passed} />

          <h1 className="mt-3 font-display text-2xl font-semibold dark:text-slate-100">
            {attempt.passed ? t('quizzes.passed') : t('quizzes.failed')}
          </h1>
          <p className="mt-1 text-sm text-ink-700/60 dark:text-slate-400">
            {t('quizzes.completed', { score: attempt.score })}
          </p>

          {certificate && (
            <div className="mt-5 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-800 dark:bg-emerald-900/20 dark:text-emerald-300">
              {t('quizzes.certificateNo')}: <strong>{certificate.certificate_number}</strong>
            </div>
          )}

          <div className="mt-6 flex justify-center gap-3">
            <Link to="/quizzes" className="btn-secondary">
              {t('quizzes.title')}
            </Link>
            {certificate ? (
              <Link to="/quizzes/certificates" className="btn-primary">
                {t('quizzes.certificates')}
              </Link>
            ) : (
              <button
                type="button"
                className="btn-primary"
                onClick={() => {
                  setResult(null);
                  setAnswers({});
                  setCurrentQIdx(0);
                }}
              >
                {t('quizzes.tryAgain')}
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  const total = quiz.questions.length;
  const answeredCount = Object.keys(answers).length;
  const allAnswered = quiz.questions.every((q) => answers[q.id]);

  return (
    <div className="mx-auto max-w-2xl">
      <Link
        to="/quizzes"
        className="mb-5 inline-flex items-center gap-1 text-sm font-semibold text-brand-700 hover:underline dark:text-brand-400"
      >
        <ChevronLeft className="h-4 w-4" />
        {t('quizzes.title')}
      </Link>

      {fromCache && (
        <div className="mb-4">
          <Alert kind="warning">{t('offline.cachedQuiz')}</Alert>
        </div>
      )}
      {!online && (
        <div className="mb-4">
          <Alert kind="warning">{t('offline.quizOfflineHint')}</Alert>
        </div>
      )}

      <h1 className="font-display text-3xl font-semibold dark:text-slate-100">{quiz.title}</h1>
      <p className="mt-2 text-ink-700/75 dark:text-slate-400">{quiz.description}</p>

      {error && (
        <div className="mt-4">
          <Alert>{error}</Alert>
        </div>
      )}

      <div className="mt-8">
        <QuizProgress current={currentQIdx} total={total} answeredCount={answeredCount} />
        <div className="space-y-4">
          {quiz.questions.map((q, idx) => (
            <div
              key={q.id}
              className="quiz-stage"
              onClick={() => setCurrentQIdx(idx)}
            >
              <p className="font-display text-base font-semibold text-ink-900 dark:text-slate-100">
                {idx + 1}. {q.question_text}
              </p>
              <div className="mt-4 space-y-2">
                {(q.displayOptions ?? []).map((opt) => (
                  <label
                    key={opt.value}
                    className={`flex cursor-pointer items-center gap-3 rounded-xl border px-4 py-3 text-sm transition-colors ${
                      answers[q.id] === opt.value
                        ? 'border-brand-500 bg-brand-50 dark:border-brand-400 dark:bg-brand-900/30'
                        : 'border-ink-100 hover:bg-ink-50/80 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700/60'
                    }`}
                  >
                    <input
                      type="radio"
                      name={q.id}
                      value={opt.value}
                      checked={answers[q.id] === opt.value}
                      onChange={() => setAnswer(q.id, opt.value)}
                      className="text-brand-600"
                    />
                    {opt.label}
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <button
        type="button"
        className="btn-primary mt-8 w-full"
        disabled={!allAnswered || submitAttempt.isPending}
        onClick={() => {
          setError('');
          submitAttempt.mutate();
        }}
      >
        {submitAttempt.isPending
          ? t('common.loading')
          : online
            ? t('quizzes.submit')
            : t('offline.queueSubmit')}
      </button>
    </div>
  );
}
