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
    is_active: form.is_active,
    questions: form.questions.map((q, index) => {
      const options =
        q.question_type === 'true_false' ? ['True', 'False'] : optionsFromText(q.optionsText);
      const options_ar =
        q.question_type === 'true_false' ? [] : optionsFromText(q.optionsTextAr);
      return {
        question_text: q.question_text,
        question_text_ar: q.question_text_ar,
        question_type: q.question_type,
        options,
        options_ar,
        correct_answer: q.correct_answer,
        points: Number(q.points) || 1,
        order: index,
      };
    }),
  };
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
                  <span className="text-sm font-medium text-gray-500">
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
                  <label className="label">{t('quizzes.fieldQuestion')}</label>
                  <textarea
                    className="input min-h-[60px]"
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
                {q.question_type === 'mcq' && (
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
                        placeholder={t('quizzes.optionsPlaceholder')}
                        value={q.optionsTextAr}
                        onChange={(e) => updateQuestion(index, { optionsTextAr: e.target.value })}
                      />
                    </div>
                  </>
                )}
                <div>
                  <label className="label">{t('quizzes.fieldCorrectAnswer')}</label>
                  {q.question_type === 'mcq' ? (
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
                  ) : (
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
                  )}
                </div>
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
