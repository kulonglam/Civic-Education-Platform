import { quizService } from '../services';
import type { Id, Quiz, QuizAnswers } from '../../types/api';
import { getDb, getEntry, scopeKey, setEntry } from './db';

type QuizQueueItem = {
  id?: number;
  quizId: Id;
  answers: QuizAnswers;
  queuedAt: number;
};

export async function loadQuiz(id: Id | undefined) {
  if (!id) throw new Error('Missing quiz id');
  const cacheKey = scopeKey(id);
  try {
    const { data } = await quizService.get(id);
    await setEntry('quizzes', cacheKey, data);
    return { data, source: 'network' as const };
  } catch (error) {
    const cached = await getEntry<Quiz>('quizzes', cacheKey);
    if (cached) {
      return { data: cached, source: 'cache' as const };
    }
    throw error;
  }
}

export async function queueQuizAttempt(quizId: Id | undefined, answers: QuizAnswers) {
  if (!quizId) throw new Error('Missing quiz id');
  const db = await getDb();
  const id = await db.add('quiz_queue', {
    quizId,
    answers,
    queuedAt: Date.now(),
  });
  return id;
}

export async function getQueuedQuizCount() {
  const db = await getDb();
  return db.count('quiz_queue');
}

export async function flushQuizQueue() {
  if (!navigator.onLine) {
    return { synced: 0, pending: await getQueuedQuizCount() };
  }

  const db = await getDb();
  const items = (await db.getAll('quiz_queue')) as QuizQueueItem[];
  let synced = 0;

  for (const item of items) {
    try {
      await quizService.attempt(item.quizId, item.answers);
      if (item.id != null) await db.delete('quiz_queue', item.id);
      synced += 1;
    } catch {
      break;
    }
  }

  const pending = await getQueuedQuizCount();
  if (synced > 0) {
    window.dispatchEvent(new CustomEvent('cep:quiz-queue-flushed', { detail: { synced, pending } }));
  }
  return { synced, pending };
}
