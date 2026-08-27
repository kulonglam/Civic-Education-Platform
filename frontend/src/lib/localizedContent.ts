import i18n from '../i18n';
import { normalizeLanguage } from '../i18n/languages';

export function contentLanguage(lang = i18n.language) {
  return normalizeLanguage(lang);
}

/** Pick ``field`` or ``field_ar`` based on UI language, falling back to English. */
export function localizedField(item, field, lang = i18n.language) {
  if (!item) return '';
  const arField = `${field}_ar`;
  if (contentLanguage(lang) === 'ar' && item[arField]) {
    return item[arField];
  }
  return item[field] ?? '';
}

export function localizedCategory(category, lang = i18n.language) {
  if (!category) return '';
  return localizedField(category, 'name', lang);
}

/** MCQ option labels localized; values stay English for API grading. */
export function localizedQuestionOptions(question, lang = i18n.language) {
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

export function localizedQuestion(question, lang = i18n.language) {
  if (!question) return question;
  return {
    ...question,
    question_text: localizedField(question, 'question_text', lang),
    displayOptions: localizedQuestionOptions(question, lang),
  };
}

export function localizedQuiz(quiz, lang = i18n.language) {
  if (!quiz) return quiz;
  return {
    ...quiz,
    title: localizedField(quiz, 'title', lang),
    description: localizedField(quiz, 'description', lang),
    questions: (quiz.questions ?? []).map((q) => localizedQuestion(q, lang)),
  };
}

export function localizedArticle(article, lang = i18n.language) {
  if (!article) return article;
  return {
    ...article,
    title: localizedField(article, 'title', lang),
    content: localizedField(article, 'content', lang),
    category: article.category
      ? { ...article.category, name: localizedCategory(article.category, lang) }
      : article.category,
  };
}

export function localizedNews(item, lang = i18n.language) {
  if (!item) return item;
  return {
    ...item,
    title: localizedField(item, 'title', lang),
    body: localizedField(item, 'body', lang),
  };
}

export function localizedEvent(item, lang = i18n.language) {
  if (!item) return item;
  return {
    ...item,
    title: localizedField(item, 'title', lang),
    description: localizedField(item, 'description', lang),
    location: localizedField(item, 'location', lang),
  };
}

/** True/false answers stay English for API grading; labels are localized. */
export function trueFalseOptions(lang = i18n.language) {
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
