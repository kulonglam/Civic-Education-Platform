import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Alert, PageHeader, Spinner } from '../components/ui';
import { ChevronLeft } from '../components/Icons';
import { extractError } from '../lib/api';
import { quizService } from '../lib/services';

function emptyQuestion(order = 0) {
  return {
    question_text: '',
    question_text_ar: '',
    question_type: 'mcq',
    optionsText: 'Option A, Option B, Option C, Option D',
    optionsTextAr: '',
    correct_answer: '',
    explanation: '',
    explanation_ar: '',
    optionFeedback: ['', '', '', ''],
    optionFeedbackAr: ['', '', '', ''],
    points: 1,
    order,
  };
}

function optionsFromText(text) {
  return text
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
}

function questionFromApi(q, index) {
  const options = Array.isArray(q.options) ? q.options : [];
  const optionsAr = Array.isArray(q.options_ar) ? q.options_ar : [];
  return {
    question_text: q.question_text ?? '',
    question_text_ar: q.question_text_ar ?? '',
    question_type: q.question_type ?? 'mcq',
    optionsText: options.join(', '),
    optionsTextAr: optionsAr.join(', '),
    correct_answer: q.correct_answer ?? '',
    explanation: q.explanation ?? '',
    explanation_ar: q.explanation_ar ?? '',
    optionFeedback: Array.isArray(q.option_feedback)
      ? q.option_feedback.map((entry) => (typeof entry === 'string' ? entry : entry?.en ?? ''))
      : [],
    optionFeedbackAr: Array.isArray(q.option_feedback)
      ? q.option_feedback.map((entry) => (typeof entry === 'string' ? '' : entry?.ar ?? ''))
      : [],
    points: q.points ?? 1,
    order: q.order ?? index,
  };
}

function buildPayload(form) {
  return {
    title: form.title,
    title_ar: form.title_ar,
    description: form.description,
    description_ar: form.description_ar,
    passing_score: Number(form.passing_score) || 70,
    kind: form.kind || 'assessment',
    feedback_mode: form.kind === 'practice' ? form.feedback_mode : 'end',
    max_attempts: form.max_attempts === '' || form.max_attempts == null
      ? null
      : Number(form.max_attempts),
    is_active: form.is_active,
    questions: form.questions.map((q, index) => {
      const options =
        q.question_type === 'true_false' ? ['True', 'False'] : optionsFromText(q.optionsText);
      const options_ar =
        q.question_type === 'true_false'
          ? optionsFromText(q.optionsTextAr).length === 2
            ? optionsFromText(q.optionsTextAr)
            : ['صحيح', 'خطأ']
          : optionsFromText(q.optionsTextAr);
      const option_feedback =
        q.question_type === 'true_false'
          ? []
          : options.map((_, i) => ({
              en: (q.optionFeedback ?? [])[i] || '',
              ar: (q.optionFeedbackAr ?? [])[i] || '',
            }));
      return {
        question_text: q.question_text,
        question_text_ar: q.question_text_ar,
        question_type: q.question_type,
        options,
        options_ar,
        correct_answer: q.correct_answer,
        explanation: q.explanation,
        explanation_ar: q.explanation_ar,
        option_feedback,
        points: Number(q.points) || 1,
        order: index,
      };
    }),
  };
}

function optionsArMismatch(q) {
  if (q.question_type === 'true_false') return false;
  const en = optionsFromText(q.optionsText);
  const ar = optionsFromText(q.optionsTextAr);
  return ar.length > 0 && ar.length !== en.length;
}

export function QuizEditorPage() {
  const { t } = useTranslation();
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);
  const [form, setForm] = useState({
    title: '',
    title_ar: '',
    description: '',
    description_ar: '',
    passing_score: 70,
    kind: 'assessment',
    feedback_mode: 'end',
    max_attempts: '',
    is_active: true,
    questions: [emptyQuestion()],
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) {
      setLoading(false);
      return;
    }
    (async () => {
      setLoading(true);
      setError('');
      try {
        const { data: quiz } = await quizService.get(id);
        setForm({
          title: quiz.title ?? '',
          title_ar: quiz.title_ar ?? '',
          description: quiz.description ?? '',
          description_ar: quiz.description_ar ?? '',
          passing_score: quiz.passing_score ?? 70,
          kind: quiz.kind ?? 'assessment',
          feedback_mode: quiz.feedback_mode ?? 'end',
          max_attempts: quiz.max_attempts ?? '',
          is_active: quiz.is_active ?? true,
          questions:
            quiz.questions?.length > 0
              ? quiz.questions.map(questionFromApi)
              : [emptyQuestion()],
        });
      } catch (err) {
        setError(extractError(err));
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  const updateQuestion = (index, patch) => {
    setForm((prev) => ({
      ...prev,
      questions: prev.questions.map((q, i) => (i === index ? { ...q, ...patch } : q)),
    }));
  };

  const addQuestion = () => {
    setForm((prev) => ({
      ...prev,
      questions: [...prev.questions, emptyQuestion(prev.questions.length)],
    }));
  };

  const removeQuestion = (index) => {
    setForm((prev) => ({
      ...prev,
      questions: prev.questions.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    const mismatched = form.questions.find(optionsArMismatch);
    if (mismatched) {
      setError(t('quizzes.optionsArMismatch'));
      setSaving(false);
      return;
    }
    try {
      const payload = buildPayload(form);
      if (isEdit) {
        await quizService.update(id, payload);
      } else {
        await quizService.create(payload);
      }
      navigate('/quizzes/manage');
    } catch (err) {
      setError(extractError(err));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Spinner />;

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader
        title={isEdit ? t('quizzes.editTitle') : t('quizzes.createTitle')}
        subtitle={isEdit ? t('quizzes.editSubtitle') : t('quizzes.createSubtitle')}
      />
      <Link to="/quizzes/manage" className="mb-4 inline-flex items-center gap-1 text-sm text-brand-600 hover:underline dark:text-brand-400">
        <ChevronLeft className="h-4 w-4" />
        {t('quizzes.manageTitle')}
      </Link>

      {error && (
        <div className="mb-4">
          <Alert>{error}</Alert>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="card space-y-4">
          <div>
            <label className="label">{t('quizzes.fieldTitle')}</label>
            <input
              className="input"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="label">{t('quizzes.fieldTitleAr')}</label>
            <input
              className="input"
              value={form.title_ar}
              onChange={(e) => setForm({ ...form, title_ar: e.target.value })}
            />
          </div>
          <div>
            <label className="label">{t('quizzes.fieldDescription')}</label>
            <textarea
              className="input min-h-[80px]"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">{t('quizzes.fieldKind')}</label>
              <select
                className="input"
                value={form.kind}
                onChange={(e) => setForm({
                  ...form,
                  kind: e.target.value,
                  feedback_mode: e.target.value === 'assessment' ? 'end' : form.feedback_mode,
                })}
              >
                <option value="assessment">{t('quizzes.kindAssessment')}</option>
                <option value="practice">{t('quizzes.kindPractice')}</option>
              </select>
              {form.kind === 'practice' && (
                <p className="mt-1 text-xs text-ink-700/60 dark:text-slate-400">
                  {t('quizzes.kindHintPractice')}
                </p>
              )}
            </div>
            <div>
              <label className="label">{t('quizzes.fieldFeedbackMode')}</label>
              <select
                className="input"
                value={form.kind === 'practice' ? form.feedback_mode : 'end'}
                disabled={form.kind !== 'practice'}
                onChange={(e) => setForm({ ...form, feedback_mode: e.target.value })}
              >
                <option value="end">{t('quizzes.feedbackEnd')}</option>
                <option value="per_question">{t('quizzes.feedbackPerQuestion')}</option>
              </select>
              <p className="mt-1 text-xs text-ink-700/60 dark:text-slate-400">
                {t('quizzes.feedbackHint')}
              </p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">{t('quizzes.passingScore')}</label>
              <input
                type="number"
                min={1}
                max={100}
                className="input"
                value={form.passing_score}
                onChange={(e) => setForm({ ...form, passing_score: e.target.value })}
              />
            </div>
            <div>
              <label className="label">{t('quizzes.fieldMaxAttempts')}</label>
              <input
                type="number"
                min={1}
                className="input"
                placeholder={t('quizzes.maxAttemptsUnlimited')}
                value={form.max_attempts}
                onChange={(e) => setForm({ ...form, max_attempts: e.target.value })}
              />
              <p className="mt-1 text-xs text-ink-700/60 dark:text-slate-400">
                {t('quizzes.maxAttemptsHint')}
              </p>
            </div>
          </div>
          <div className="flex items-end">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
              />
              {t('quizzes.fieldActive')}
            </label>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">{t('quizzes.questionsSection')}</h2>
            <button type="button" className="btn-secondary text-sm" onClick={addQuestion}>
              {t('quizzes.addQuestion')}
            </button>
          </div>

          {form.questions.map((q, index) => {
            const options =
              q.question_type === 'true_false' ? ['True', 'False'] : optionsFromText(q.optionsText);
            return (
              <div key={index} className="card space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-ink-700/60">
                    {t('quizzes.questionNumber', { n: index + 1 })}
                  </span>
                  {form.questions.length > 1 && (
                    <button
                      type="button"
                      className="text-xs text-red-600 hover:underline"
                      onClick={() => removeQuestion(index)}
                    >
                      {t('common.delete')}
                    </button>
                  )}
                </div>
                <div>
                  <label className="label">
                    {q.question_type === 'scenario' ? t('quizzes.fieldSituation') : t('quizzes.fieldQuestion')}
                  </label>
                  <textarea
                    className={`input ${q.question_type === 'scenario' ? 'min-h-[120px]' : 'min-h-[60px]'}`}
                    value={q.question_text}
                    onChange={(e) => updateQuestion(index, { question_text: e.target.value })}
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="label">{t('quizzes.fieldType')}</label>
                    <select
                      className="input"
                      value={q.question_type}
                      onChange={(e) =>
                        updateQuestion(index, {
                          question_type: e.target.value,
                          optionsText:
                            e.target.value === 'true_false'
                              ? 'True, False'
                              : q.optionsText,
                          correct_answer: '',
                        })
                      }
                    >
                      <option value="mcq">{t('quizzes.typeMcq')}</option>
                      <option value="true_false">{t('quizzes.typeTrueFalse')}</option>
                      <option value="scenario">{t('quizzes.typeScenario')}</option>
                    </select>
                  </div>
                  <div>
                    <label className="label">{t('quizzes.fieldPoints')}</label>
                    <input
                      type="number"
                      min={1}
                      className="input"
                      value={q.points}
                      onChange={(e) => updateQuestion(index, { points: e.target.value })}
                    />
                  </div>
                </div>
                {(q.question_type === 'mcq' || q.question_type === 'scenario') && (
                  <>
                    <div>
                      <label className="label">{t('quizzes.fieldOptions')}</label>
                      <input
                        className="input"
                        placeholder={t('quizzes.optionsPlaceholder')}
                        value={q.optionsText}
                        onChange={(e) => updateQuestion(index, { optionsText: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="label">{t('quizzes.fieldOptionsAr')}</label>
                      <input
                        className="input"
                        dir="rtl"
                        placeholder={t('quizzes.optionsArPlaceholder')}
                        value={q.optionsTextAr}
                        onChange={(e) => updateQuestion(index, { optionsTextAr: e.target.value })}
                      />
                      {optionsArMismatch(q) && (
                        <p className="mt-1 text-xs text-amber-700 dark:text-amber-400">
                          {t('quizzes.optionsArMismatch')}
                        </p>
                      )}
                    </div>
                  </>
                )}
                {q.question_type === 'true_false' && (
                  <div>
                    <label className="label">{t('quizzes.fieldOptionsAr')}</label>
                    <input
                      className="input"
                      dir="rtl"
                      placeholder={t('quizzes.trueFalseArPlaceholder')}
                      value={q.optionsTextAr}
                      onChange={(e) => updateQuestion(index, { optionsTextAr: e.target.value })}
                    />
                    <p className="mt-1 text-xs text-ink-700/60 dark:text-slate-400">
                      {t('quizzes.trueFalseArHint')}
                    </p>
                  </div>
                )}
                <div>
                  <label className="label">{t('quizzes.fieldQuestionAr')}</label>
                  <textarea
                    className="input min-h-[60px]"
                    dir="rtl"
                    value={q.question_text_ar}
                    onChange={(e) => updateQuestion(index, { question_text_ar: e.target.value })}
                  />
                </div>
                <div>
                  <label className="label">{t('quizzes.fieldCorrectAnswer')}</label>
                  {q.question_type === 'true_false' ? (
                    <select
                      className="input"
                      value={q.correct_answer}
                      onChange={(e) => updateQuestion(index, { correct_answer: e.target.value })}
                      required
                    >
                      <option value="">{t('quizzes.selectAnswer')}</option>
                      <option value="True">True</option>
                      <option value="False">False</option>
                    </select>
                  ) : (
                    <select
                      className="input"
                      value={q.correct_answer}
                      onChange={(e) => updateQuestion(index, { correct_answer: e.target.value })}
                      required
                    >
                      <option value="">{t('quizzes.selectAnswer')}</option>
                      {options.map((opt) => (
                        <option key={opt} value={opt}>
                          {opt}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
                {q.question_type === 'scenario' ? (
                  <div className="space-y-3">
                    <p className="text-sm font-medium text-ink-800 dark:text-slate-200">
                      {t('quizzes.optionFeedbackHint')}
                    </p>
                    {options.map((opt, optIndex) => (
                      <div key={`${opt}-${optIndex}`} className="space-y-2 rounded-xl border border-ink-100 p-3 dark:border-slate-700">
                        <p className="text-xs font-semibold text-ink-700/70 dark:text-slate-400">{opt || t('quizzes.optionN', { n: optIndex + 1 })}</p>
                        <textarea
                          className="input min-h-[72px]"
                          placeholder={t('quizzes.optionFeedbackEn')}
                          value={(q.optionFeedback ?? [])[optIndex] || ''}
                          onChange={(e) => {
                            const next = [...(q.optionFeedback ?? [])];
                            next[optIndex] = e.target.value;
                            updateQuestion(index, { optionFeedback: next });
                          }}
                        />
                        <textarea
                          className="input min-h-[72px]"
                          dir="rtl"
                          placeholder={t('quizzes.optionFeedbackAr')}
                          value={(q.optionFeedbackAr ?? [])[optIndex] || ''}
                          onChange={(e) => {
                            const next = [...(q.optionFeedbackAr ?? [])];
                            next[optIndex] = e.target.value;
                            updateQuestion(index, { optionFeedbackAr: next });
                          }}
                        />
                      </div>
                    ))}
                  </div>
                ) : (
                  <>
                    <div>
                      <label className="label">{t('quizzes.fieldExplanation')}</label>
                      <textarea
                        className="input min-h-[60px]"
                        value={q.explanation}
                        onChange={(e) => updateQuestion(index, { explanation: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="label">{t('quizzes.fieldExplanationAr')}</label>
                      <textarea
                        className="input min-h-[60px]"
                        dir="rtl"
                        value={q.explanation_ar}
                        onChange={(e) => updateQuestion(index, { explanation_ar: e.target.value })}
                      />
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>

        <div className="flex flex-wrap gap-3">
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? t('common.loading') : t('common.save')}
          </button>
          <Link to="/quizzes/manage" className="btn-secondary">
            {t('common.cancel')}
          </Link>
        </div>
      </form>
    </div>
  );
}
