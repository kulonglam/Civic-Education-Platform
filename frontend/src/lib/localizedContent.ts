import i18n from '../i18n';
import { normalizeLanguage } from '../i18n/languages';
import type { Article, Category, CivicEvent, CivicNews, Question, Quiz } from '../types/api';

export function contentLanguage(lang: string | null | undefined = i18n.language) {
  return normalizeLanguage(lang);
}

/** Pick ``field`` or ``field_ar`` based on UI language, falling back to English. */
export function localizedField(item: object | null | undefined, field: string, lang: string | null | undefined = i18n.language) {
  if (!item) return '';
  const record = item as Record<string, unknown>;
  const arField = `${field}_ar`;
  if (contentLanguage(lang) === 'ar' && record[arField]) {
    return String(record[arField] ?? '');
  }
  return record[field] == null ? '' : String(record[field]);
}

export function localizedCategory(category: Category | null | undefined, lang: string | null | undefined = i18n.language) {
  if (!category) return '';
  return localizedField(category, 'name', lang);
}

/** MCQ option labels localized; values stay English for API grading. */
export function localizedQuestionOptions(question: Question | null | undefined, lang: string | null | undefined = i18n.language) {
  if (!question) return [];
  if (question.question_type === 'true_false') {
    const options = question.options ?? [];
    const optionsAr = question.options_ar ?? [];
    if (contentLanguage(lang) === 'ar' && optionsAr.length === options.length && options.length > 0) {
      return options.map((opt, index) => ({
        value: opt,
        label: optionsAr[index] ?? opt,
      }));
    }
    return trueFalseOptions(lang);
  }
  const options = question.options ?? [];
  const optionsAr = question.options_ar ?? [];
  if (contentLanguage(lang) === 'ar' && optionsAr.length) {
    return options.map((opt, index) => ({
      value: opt,
      label: optionsAr[index] ?? opt,
    }));
  }
  return options.map((opt) => ({ value: opt, label: opt }));
}

export function localizedQuestion<T extends Question>(question: T, lang: string | null | undefined = i18n.language) {
  return {
    ...question,
    question_text: localizedField(question, 'question_text', lang),
    displayOptions: localizedQuestionOptions(question, lang),
  };
}

export function localizedQuiz<T extends Quiz>(quiz: T, lang: string | null | undefined = i18n.language) {
  return {
    ...quiz,
    title: localizedField(quiz, 'title', lang),
    description: localizedField(quiz, 'description', lang),
    questions: (quiz.questions ?? []).map((q) => localizedQuestion(q, lang)),
  };
}

export function localizedArticle<T extends Article>(article: T, lang: string | null | undefined = i18n.language) {
  return {
    ...article,
    title: localizedField(article, 'title', lang),
    content: localizedField(article, 'content', lang),
    category: article.category
      ? { ...article.category, name: localizedCategory(article.category, lang) }
      : article.category,
  };
}

export function localizedNews<T extends CivicNews>(item: T, lang: string | null | undefined = i18n.language) {
  return {
    ...item,
    title: localizedField(item, 'title', lang),
    body: localizedField(item, 'body', lang),
  };
}

export function localizedEvent<T extends CivicEvent>(item: T, lang: string | null | undefined = i18n.language) {
  return {
    ...item,
    title: localizedField(item, 'title', lang),
    description: localizedField(item, 'description', lang),
    location: localizedField(item, 'location', lang),
  };
}

/** True/false answers stay English for API grading; labels are localized. */
export function trueFalseOptions(lang: string | null | undefined = i18n.language) {
  if (contentLanguage(lang) === 'ar') {
    return [
      { value: 'True', label: 'صحيح' },
      { value: 'False', label: 'خطأ' },
    ];
  }
  return [
    { value: 'True', label: 'True' },
    { value: 'False', label: 'False' },
  ];
}
