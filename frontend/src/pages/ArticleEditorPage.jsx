import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Alert, PageHeader, Spinner } from '../components/ui';
import { ChevronLeft, FileText } from '../components/Icons';
import { extractError } from '../lib/api';
import { renderMarkdown } from '../lib/markdown';
import { resolveMediaUrl } from '../lib/media';
import { articleService, categoryService } from '../lib/services';

const EMPTY_FORM = {
  title: '',
  title_ar: '',
  content: '',
  content_ar: '',
  category_id: '',
  tags: '',
  featured_image_url: '',
  attachment_url: '',
  attachment_name: '',
  status: 'draft',
};

function tagsToString(tags) {
  return Array.isArray(tags) ? tags.join(', ') : '';
}

function tagsFromString(value) {
  return value
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean);
}

export function ArticleEditorPage() {
  const { t } = useTranslation();
  const { id } = useParams();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const isEdit = Boolean(id);
  const [form, setForm] = useState(EMPTY_FORM);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    (async () => {
      setLoading(true);
      setError('');
      try {
        const { data: cats } = await categoryService.list();
        const list = cats.results ?? cats;
        setCategories(list);

        if (id) {
          const { data: article } = await articleService.get(id);
          setForm({
            title: article.title ?? '',
            title_ar: article.title_ar ?? '',
            content: article.content ?? '',
            content_ar: article.content_ar ?? '',
            category_id: article.category?.id ?? '',
            tags: tagsToString(article.tags),
            featured_image_url: article.featured_image_url ?? '',
            attachment_url: article.attachment_url ?? '',
            attachment_name: article.attachment_name ?? '',
            status: article.status ?? 'draft',
          });
        } else if (list.length > 0) {
          setForm((prev) => ({ ...prev, category_id: list[0].id }));
        }
      } catch (err) {
        setError(extractError(err));
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  const uploadAttachment = async (file) => {
    setUploading(true);
    setError('');
    try {
      const { data } = await articleService.uploadAttachment(file);
      setForm((prev) => ({
        ...prev,
        attachment_url: data.attachment_url,
        attachment_name: data.attachment_name,
      }));
    } catch (err) {
      setError(extractError(err));
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleAttachmentChange = (e) => {
    const file = e.target.files?.[0];
    if (file) uploadAttachment(file);
  };

  const removeAttachment = () => {
    setForm((prev) => ({ ...prev, attachment_url: '', attachment_name: '' }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const payload = {
        title: form.title,
        title_ar: form.title_ar,
        content: form.content,
        content_ar: form.content_ar,
        category_id: form.category_id,
        tags: tagsFromString(form.tags),
        featured_image_url: form.featured_image_url,
        attachment_url: form.attachment_url,
        attachment_name: form.attachment_name,
        status: form.status,
      };
      if (isEdit) {
        await articleService.update(id, payload);
      } else {
        await articleService.create(payload);
      }
      navigate('/articles/manage');
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
        title={isEdit ? t('articles.editTitle') : t('articles.createTitle')}
        subtitle={isEdit ? t('articles.editSubtitle') : t('articles.createSubtitle')}
      />
      <Link to="/articles/manage" className="mb-4 inline-flex items-center gap-1 text-sm text-brand-600 hover:underline dark:text-brand-400">
        <ChevronLeft className="h-4 w-4" />
        {t('articles.manageTitle')}
      </Link>

      {error && (
        <div className="mb-4">
          <Alert>{error}</Alert>
        </div>
      )}

      <form onSubmit={handleSubmit} className="card space-y-4">
        <div>
          <label className="label">{t('articles.fieldTitle')}</label>
          <input
            className="input"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            required
          />
        </div>
        <div>
          <label className="label">{t('articles.fieldTitleAr')}</label>
          <input
            className="input"
            value={form.title_ar}
            onChange={(e) => setForm({ ...form, title_ar: e.target.value })}
          />
        </div>
        <div>
          <label className="label">{t('articles.category')}</label>
          <select
            className="input"
            value={form.category_id}
            onChange={(e) => setForm({ ...form, category_id: e.target.value })}
            required
          >
            <option value="">{t('articles.selectCategory')}</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="label">{t('articles.fieldStatus')}</label>
          <select
            className="input"
            value={form.status}
            onChange={(e) => setForm({ ...form, status: e.target.value })}
          >
            <option value="draft">{t('articles.statusDraft')}</option>
            <option value="published">{t('articles.statusPublished')}</option>
            <option value="archived">{t('articles.statusArchived')}</option>
          </select>
        </div>
        <div>
          <div className="mb-2 flex items-center justify-between gap-2">
            <label className="label mb-0">{t('articles.fieldContent')}</label>
            <button
              type="button"
              className="text-sm text-brand-600 hover:underline dark:text-brand-400"
              onClick={() => setShowPreview((v) => !v)}
            >
              {showPreview ? t('articles.hidePreview') : t('articles.showPreview')}
            </button>
          </div>
          <p className="mb-2 text-xs text-gray-500 dark:text-slate-400">{t('articles.markdownHint')}</p>
          {!showPreview ? (
            <textarea
              className="input min-h-[160px]"
              value={form.content}
              onChange={(e) => setForm({ ...form, content: e.target.value })}
              required
            />
          ) : (
            <div
              className="prose min-h-[160px] max-w-none rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-slate-600 dark:bg-slate-900"
              dangerouslySetInnerHTML={{ __html: renderMarkdown(form.content) }}
            />
          )}
        </div>
        <div>
          <label className="label">{t('articles.fieldContentAr')}</label>
          <textarea
            className="input min-h-[160px]"
            value={form.content_ar}
            onChange={(e) => setForm({ ...form, content_ar: e.target.value })}
          />
        </div>
        <div>
          <label className="label">{t('articles.fieldTags')}</label>
          <input
            className="input"
            placeholder={t('articles.tagsPlaceholder')}
            value={form.tags}
            onChange={(e) => setForm({ ...form, tags: e.target.value })}
          />
        </div>
        <div>
          <label className="label">{t('articles.fieldImage')}</label>
          <input
            className="input"
            type="url"
            value={form.featured_image_url}
            onChange={(e) => setForm({ ...form, featured_image_url: e.target.value })}
          />
        </div>
        <div>
          <label className="label">{t('articles.fieldAttachment')}</label>
          <p className="mb-2 text-xs text-gray-500 dark:text-slate-400">{t('articles.attachmentHint')}</p>
          {form.attachment_url ? (
            <div className="flex flex-wrap items-center gap-3 rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 dark:border-slate-600 dark:bg-slate-900">
              <FileText className="h-5 w-5 shrink-0 text-brand-600 dark:text-brand-400" />
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-slate-400">
                  {t('articles.attachmentCurrent')}
                </p>
                <a
                  href={resolveMediaUrl(form.attachment_url)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="truncate text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
                >
                  {form.attachment_name || form.attachment_url}
                </a>
              </div>
              <button type="button" className="btn-secondary text-sm" onClick={removeAttachment}>
                {t('articles.attachmentRemove')}
              </button>
            </div>
          ) : (
            <div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                className="input"
                onChange={handleAttachmentChange}
                disabled={uploading}
              />
              {uploading && (
                <p className="mt-1 text-xs text-gray-500 dark:text-slate-400">{t('articles.attachmentUploading')}</p>
              )}
            </div>
          )}
        </div>
        <div className="flex flex-wrap gap-3">
          <button type="submit" className="btn-primary" disabled={saving || uploading}>
            {saving ? t('common.loading') : t('common.save')}
          </button>
          <Link to="/articles/manage" className="btn-secondary">
            {t('common.cancel')}
          </Link>
        </div>
      </form>
    </div>
  );
}
