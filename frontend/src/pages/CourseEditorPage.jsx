import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import { Alert, PageHeader, Spinner } from '../components/ui';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { articleService, courseService } from '../lib/services';

const emptyForm = {
  title: '',
  title_ar: '',
  slug: '',
  description: '',
  description_ar: '',
  status: 'draft',
  lesson_ids: [],
};

export function CourseEditorPage() {
  const { t } = useTranslation();
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const { data: articles = [] } = useQuery({
    queryKey: ['articles', 'course-picker'],
    queryFn: async () => {
      const { data } = await articleService.list({ status: 'published', page_size: '100' });
      return data.results ?? data;
    },
  });

  useEffect(() => {
    if (!isEdit) return undefined;
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const { data } = await courseService.get(id, { manage: '1' });
        if (cancelled) return;
        setForm({
          title: data.title ?? '',
          title_ar: data.title_ar ?? '',
          slug: data.slug ?? '',
          description: data.description ?? '',
          description_ar: data.description_ar ?? '',
          status: data.status ?? 'draft',
          lesson_ids: (data.lessons || []).map((lesson) => lesson.article_id),
        });
      } catch (err) {
        if (!cancelled) setError(extractError(err));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [id, isEdit]);

  const setField = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const toggleLesson = (articleId) => {
    setForm((prev) => {
      const exists = prev.lesson_ids.includes(articleId);
      return {
        ...prev,
        lesson_ids: exists
          ? prev.lesson_ids.filter((value) => value !== articleId)
          : [...prev.lesson_ids, articleId],
      };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      if (isEdit) await courseService.update(id, form);
      else await courseService.create(form);
      navigate('/courses/manage');
    } catch (err) {
      setError(extractError(err));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Spinner />;

  return (
    <div className="page-shell">
      <PageHeader
        eyebrow={t('nav.manage')}
        title={isEdit ? t('courses.editTitle') : t('courses.create')}
        subtitle={t('courses.editorHint')}
      />
      {error && <Alert>{error}</Alert>}
      <form className="mt-6 grid gap-4" onSubmit={handleSubmit}>
        <label className="grid gap-1 text-sm font-medium">
          {t('courses.fields.title')}
          <input className="input" required value={form.title} onChange={(e) => setField('title', e.target.value)} />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('courses.fields.titleAr')}
          <input className="input" value={form.title_ar} onChange={(e) => setField('title_ar', e.target.value)} />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('courses.fields.slug')}
          <input className="input" required value={form.slug} onChange={(e) => setField('slug', e.target.value)} />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('courses.fields.description')}
          <textarea className="input min-h-[6rem]" value={form.description} onChange={(e) => setField('description', e.target.value)} />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('courses.fields.descriptionAr')}
          <textarea className="input min-h-[6rem]" value={form.description_ar} onChange={(e) => setField('description_ar', e.target.value)} />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('courses.fields.status')}
          <select className="input" value={form.status} onChange={(e) => setField('status', e.target.value)}>
            <option value="draft">{t('courses.status.draft')}</option>
            <option value="published">{t('courses.status.published')}</option>
            <option value="archived">{t('courses.status.archived')}</option>
          </select>
        </label>
        <fieldset className="grid gap-2">
          <legend className="text-sm font-medium">{t('courses.fields.lessons')}</legend>
          <p className="text-xs text-ink-700/60 dark:text-slate-400">{t('courses.lessonsHint')}</p>
          <ul className="max-h-72 space-y-1 overflow-auto rounded-xl border border-ink-100 p-3 dark:border-slate-700">
            {articles.map((article) => (
              <li key={article.id}>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={form.lesson_ids.includes(article.id)}
                    onChange={() => toggleLesson(article.id)}
                  />
                  {article.title}
                </label>
              </li>
            ))}
          </ul>
        </fieldset>
        <div className="flex gap-2">
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? t('common.loading') : t('common.save')}
          </button>
          <button type="button" className="btn-secondary" onClick={() => navigate('/courses/manage')}>
            {t('common.cancel')}
          </button>
        </div>
      </form>
    </div>
  );
}
