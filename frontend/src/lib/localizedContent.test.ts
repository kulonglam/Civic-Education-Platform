import { describe, expect, it } from 'vitest';
import {
  contentLanguage,
  localizedArticle,
  localizedField,
  localizedQuestionOptions,
  localizedQuiz,
  trueFalseOptions,
} from './localizedContent';
import type { Article, Question, Quiz } from '../types/api';

describe('localizedContent', () => {
  const article = {
    title: 'Constitution',
    title_ar: 'الدستور',
    content: 'English body',
    content_ar: 'النص العربي',
    category: { name: 'Governance', name_ar: 'الحكم' },
  };

  it('returns English by default', () => {
    expect(localizedField(article, 'title', 'en')).toBe('Constitution');
    expect(contentLanguage('en-US')).toBe('en');
  });

  it('returns Arabic when available', () => {
    expect(localizedField(article, 'title', 'ar')).toBe('الدستور');
    expect(localizedField(article, 'content', 'ar')).toBe('النص العربي');
  });

  it('falls back to English when Arabic missing', () => {
    expect(localizedField({ title: 'Only EN' }, 'title', 'ar')).toBe('Only EN');
  });

  it('localizes nested article and quiz objects', () => {
    const localized = localizedArticle({ ...article, id: '1' } as Article, 'ar');
    expect(localized.title).toBe('الدستور');
    expect(localized.category?.name).toBe('الحكم');

    const quiz = localizedQuiz(
      {
        id: 'q1',
        title: 'Quiz',
        title_ar: 'اختبار',
        description: 'Desc',
        description_ar: 'وصف',
        questions: [{ question_text: 'Q1', question_text_ar: 'س1' }],
      } as Quiz,
      'ar',
    );
    expect(quiz.title).toBe('اختبار');
    expect(quiz.questions?.[0].question_text).toBe('س1');
  });

  it('localizes MCQ option labels in Arabic', () => {
    const opts = localizedQuestionOptions(
      {
        question_text: 'Q',
        question_type: 'mcq',
        options: ['Alpha', 'Beta'],
        options_ar: ['ألفا', 'بيتا'],
      } as Question,
      'ar',
    );
    expect(opts).toEqual([
      { value: 'Alpha', label: 'ألفا' },
      { value: 'Beta', label: 'بيتا' },
    ]);
  });

  it('uses stored Arabic true/false labels when provided', () => {
    const opts = localizedQuestionOptions(
      {
        question_text: 'Q',
        question_type: 'true_false',
        options: ['True', 'False'],
        options_ar: ['نعم', 'لا'],
      } as Question,
      'ar',
    );
    expect(opts).toEqual([
      { value: 'True', label: 'نعم' },
      { value: 'False', label: 'لا' },
    ]);
  });

  it('keeps true/false answer values in English', () => {
    const opts = trueFalseOptions('ar');
    expect(opts.map((o) => o.value)).toEqual(['True', 'False']);
    expect(opts[0].label).toBe('صحيح');
  });
});
