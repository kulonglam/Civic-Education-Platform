import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import { NEWS_CLAIM_TYPES, NEWS_TOPICS } from '../components/ClaimBadge';
import { Alert, PageHeader, Spinner } from '../components/ui';
import { extractError } from '../lib/api';
import { newsService } from '../lib/services';

const emptyForm = {
  title: '',
  title_ar: '',
  body: '',
  body_ar: '',
  topic: 'announcement',
  claim_type: 'educational',
  source_name: '',
  source_url: '',
  status: 'draft',
};

export function NewsEditorPage() {
  const { t } = useTranslation();
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isEdit) return undefined;
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const { data } = await newsService.get(id);
        if (cancelled) return;
        setForm({
          title: data.title ?? '',
          title_ar: data.title_ar ?? '',
          body: data.body ?? '',
          body_ar: data.body_ar ?? '',
          topic: data.topic ?? 'announcement',
          claim_type: data.claim_type ?? 'educational',
          source_name: data.source_name ?? '',
          source_url: data.source_url ?? '',
          status: data.status ?? 'draft',
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

  const setField = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      if (isEdit) {
        await newsService.update(id, form);
        navigate(`/news/${id}`);
      } else {
        const { data } = await newsService.create(form);
        navigate(`/news/${data.id}`);
      }
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
        title={isEdit ? t('news.editTitle') : t('news.create')}
        subtitle={t('news.editorHint')}
      />
      {error && <Alert>{error}</Alert>}
      <form className="mt-6 grid gap-4" onSubmit={handleSubmit}>
        <label className="grid gap-1 text-sm font-medium">
          {t('news.fields.title')}
          <input
            className="input"
            required
            value={form.title}
            onChange={(e) => setField('title', e.target.value)}
          />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('news.fields.titleAr')}
          <input
            className="input"
            value={form.title_ar}
            onChange={(e) => setField('title_ar', e.target.value)}
          />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('news.fields.body')}
          <textarea
            className="input min-h-[10rem]"
            required
            value={form.body}
            onChange={(e) => setField('body', e.target.value)}
          />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('news.fields.bodyAr')}
          <textarea
            className="input min-h-[8rem]"
            value={form.body_ar}
            onChange={(e) => setField('body_ar', e.target.value)}
          />
        </label>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="grid gap-1 text-sm font-medium">
            {t('news.fields.topic')}
            <select
              className="input"
              value={form.topic}
              onChange={(e) => setField('topic', e.target.value)}
            >
              {NEWS_TOPICS.map((value) => (
                <option key={value} value={value}>
                  {t(`news.topics.${value}`)}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-1 text-sm font-medium">
            {t('news.fields.claim')}
            <select
              className="input"
              value={form.claim_type}
              onChange={(e) => setField('claim_type', e.target.value)}
            >
              {NEWS_CLAIM_TYPES.map((value) => (
                <option key={value} value={value}>
                  {t(`news.claims.${value}`)}
                </option>
              ))}
            </select>
          </label>
        </div>
        {form.claim_type === 'verified_fact' && (
          <Alert kind="info">{t('news.verifiedNeedsSource')}</Alert>
        )}
        <label className="grid gap-1 text-sm font-medium">
          {t('news.fields.sourceName')}
          <input
            className="input"
            required={form.claim_type === 'verified_fact'}
            value={form.source_name}
            onChange={(e) => setField('source_name', e.target.value)}
          />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('news.fields.sourceUrl')}
          <input
            className="input"
            type="url"
            value={form.source_url}
            onChange={(e) => setField('source_url', e.target.value)}
          />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('news.fields.status')}
          <select
            className="input sm:max-w-xs"
            value={form.status}
            onChange={(e) => setField('status', e.target.value)}
          >
            <option value="draft">{t('news.status.draft')}</option>
            <option value="published">{t('news.status.published')}</option>
            <option value="archived">{t('news.status.archived')}</option>
          </select>
        </label>
        <div>
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? t('common.loading') : t('common.save')}
          </button>
        </div>
      </form>
    </div>
  );
}
