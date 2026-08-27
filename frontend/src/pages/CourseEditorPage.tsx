import { useEffect, useState, type FormEvent } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Spinner } from '../components/ui';
import { CmsEditorShell, CmsSidebarCard } from '../components/CmsWorkspace';
import { extractError } from '../lib/api';
import { articleService, courseService } from '../lib/services';
import type { CourseFormState, Id } from '../types/api';

const emptyForm = {
  title: '',
  title_ar: '',
  slug: '',
  description: '',
  description_ar: '',
  status: 'draft',
  lesson_ids: [] as any[],
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

  const setField = (key: keyof CourseFormState, value: CourseFormState[keyof CourseFormState]) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const toggleLesson = (articleId: Id) => {
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

  const handleSubmit = async (e: FormEvent) => {
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
    <form onSubmit={handleSubmit}>
      <CmsEditorShell
        backTo="/courses/manage"
        backLabel={t('courses.manageTitle')}
        title={isEdit ? t('courses.editTitle') : t('courses.create')}
        subtitle={t('courses.editorHint')}
        status={form.status}
        statusLabel={t(`courses.status.${form.status}`)}
        error={error}
        sidebar={
          <CmsSidebarCard title={t('cms.publish')}>
            <label className="label">{t('courses.fields.status')}</label>
            <select className="input" value={form.status} onChange={(e) => setField('status', e.target.value)}>
              <option value="draft">{t('courses.status.draft')}</option>
              <option value="published">{t('courses.status.published')}</option>
              <option value="archived">{t('courses.status.archived')}</option>
            </select>
            <label className="label mt-3">{t('courses.fields.slug')}</label>
            <input className="input" required value={form.slug} onChange={(e) => setField('slug', e.target.value)} />
          </CmsSidebarCard>
        }
        footer={
          <>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? t('common.loading') : t('common.save')}
            </button>
            <Link to="/courses/manage" className="btn-secondary">
              {t('common.cancel')}
            </Link>
          </>
        }
      >
        <div className="card space-y-4">
          <label className="grid gap-1 text-sm font-medium">
            {t('courses.fields.title')}
            <input className="input" required value={form.title} onChange={(e) => setField('title', e.target.value)} />
          </label>
          <label className="grid gap-1 text-sm font-medium">
            {t('courses.fields.titleAr')}
            <input className="input" value={form.title_ar} onChange={(e) => setField('title_ar', e.target.value)} />
          </label>
          <label className="grid gap-1 text-sm font-medium">
            {t('courses.fields.description')}
            <textarea className="input min-h-[6rem]" value={form.description} onChange={(e) => setField('description', e.target.value)} />
          </label>
          <label className="grid gap-1 text-sm font-medium">
            {t('courses.fields.descriptionAr')}
            <textarea className="input min-h-[6rem]" value={form.description_ar} onChange={(e) => setField('description_ar', e.target.value)} />
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
        </div>
      </CmsEditorShell>
    </form>
  );
}
