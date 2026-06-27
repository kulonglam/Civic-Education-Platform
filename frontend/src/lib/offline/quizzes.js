import { quizService } from '../services';
import { getDb, getEntry, scopeKey, setEntry } from './db';

export async function loadQuiz(id) {
  const cacheKey = scopeKey(id);
  try {
    const { data } = await quizService.get(id);
    await setEntry('quizzes', cacheKey, data);
    return { data, source: 'network' };
  } catch (error) {
    const cached = await getEntry('quizzes', cacheKey);
    if (cached) {
      return { data: cached, source: 'cache' };
    }
    throw error;
  }
}

export async function queueQuizAttempt(quizId, answers) {
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
  const items = await db.getAll('quiz_queue');
  let synced = 0;

  for (const item of items) {
    try {
      await quizService.attempt(item.quizId, item.answers);
      await db.delete('quiz_queue', item.id);
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
