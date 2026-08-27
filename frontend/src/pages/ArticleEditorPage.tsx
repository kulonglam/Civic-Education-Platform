import { useEffect, useRef, useState, type ChangeEvent, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Spinner } from '../components/ui';
import { CmsEditorShell, CmsSidebarCard } from '../components/CmsWorkspace';
import { FileText } from '../components/Icons';
import { extractError } from '../lib/api';
import { renderMarkdown } from '../lib/markdown';
import { resolveMediaUrl } from '../lib/media';
import { articleService, categoryService, mediaService } from '../lib/services';
import type { Article, Category, MediaAsset } from '../types/api';

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
  attachment_version: '',
  document_label: '',
  is_controlled_document: false,
  audio_media_id: '',
  video_media_id: '',
  status: 'draft',
};

function tagsToString(tags: Article['tags']) {
  return Array.isArray(tags) ? tags.join(', ') : '';
}

function tagsFromString(value: string) {
  return value
    .split(',')
    .map((tag: string) => tag.trim())
    .filter(Boolean);
}

function insertAroundSelection(
  textarea: HTMLTextAreaElement | null,
  before: string,
  after = '',
  placeholder = '',
) {
  if (!textarea) return null;
  const start = textarea.selectionStart ?? 0;
  const end = textarea.selectionEnd ?? 0;
  const value = textarea.value;
  const selected = value.slice(start, end) || placeholder;
  const next = `${value.slice(0, start)}${before}${selected}${after}${value.slice(end)}`;
  const cursor = start + before.length + selected.length;
  return { next, cursorStart: start + before.length, cursorEnd: cursor };
}

function MarkdownToolbar({
  onInsert,
  onUploadImage,
  uploading,
}: {
  onInsert: (before: string, after: string, placeholder: string) => void;
  onUploadImage: (file: File) => void;
  uploading: boolean;
}) {
  const { t } = useTranslation();
  const imageInputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="mb-2 flex flex-wrap items-center gap-1">
      <button type="button" className="btn-secondary px-2 py-1 text-xs font-semibold" onClick={() => onInsert('**', '**', 'bold')}>
        B
      </button>
      <button type="button" className="btn-secondary px-2 py-1 text-xs italic" onClick={() => onInsert('_', '_', 'italic')}>
        I
      </button>
      <button type="button" className="btn-secondary px-2 py-1 text-xs" onClick={() => onInsert('## ', '', 'Heading')}>
        H2
      </button>
      <button type="button" className="btn-secondary px-2 py-1 text-xs" onClick={() => onInsert('- ', '', 'List item')}>
        •
      </button>
      <button
        type="button"
        className="btn-secondary px-2 py-1 text-xs"
        onClick={() => onInsert('[', '](https://)', 'link text')}
      >
        {t('articles.mdLink')}
      </button>
      <button
        type="button"
        className="btn-secondary px-2 py-1 text-xs"
        disabled={uploading}
        onClick={() => imageInputRef.current?.click()}
      >
        {uploading ? t('common.loading') : t('articles.mdImage')}
      </button>
      <input
        ref={imageInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onUploadImage(file);
          e.target.value = '';
        }}
      />
    </div>
  );
}

export function ArticleEditorPage() {
  const { t } = useTranslation();
  const { id } = useParams();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const featuredInputRef = useRef<HTMLInputElement>(null);
  const contentRef = useRef<HTMLTextAreaElement>(null);
  const contentArRef = useRef<HTMLTextAreaElement>(null);
  const activeFieldRef = useRef('content');
  const isEdit = Boolean(id);
  const [form, setForm] = useState(EMPTY_FORM);
  const [categories, setCategories] = useState<Category[]>([]);
  const [audioOptions, setAudioOptions] = useState<MediaAsset[]>([]);
  const [videoOptions, setVideoOptions] = useState<MediaAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [imageUploading, setImageUploading] = useState(false);
  const [error, setError] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  const [previewLang, setPreviewLang] = useState('en');

  useEffect(() => {
    (async () => {
      setLoading(true);
      setError('');
      try {
        const { data: cats } = await categoryService.list();
        const list = cats.results ?? cats;
        setCategories(list);

        const [{ data: audioRes }, { data: videoRes }] = await Promise.all([
          mediaService.list({ media_type: 'audio', page_size: '100' }),
          mediaService.list({ media_type: 'video', page_size: '100' }),
        ]);
        setAudioOptions(audioRes.results ?? audioRes ?? []);
        setVideoOptions(videoRes.results ?? videoRes ?? []);

        if (id) {
          const { data: article } = await articleService.get(id);
          setForm({
            title: article.title ?? '',
            title_ar: article.title_ar ?? '',
            content: article.content ?? '',
            content_ar: article.content_ar ?? '',
            category_id: String(article.category?.id ?? ''),
            tags: tagsToString(article.tags),
            featured_image_url: article.featured_image_url ?? '',
            attachment_url: article.attachment_url ?? '',
            attachment_name: article.attachment_name ?? '',
            attachment_version: article.attachment_version ?? '',
            document_label: article.document_label ?? '',
            is_controlled_document: Boolean(article.is_controlled_document),
            audio_media_id: String(article.audio_media?.id ?? ''),
            video_media_id: String(article.video_media?.id ?? ''),
            status: article.status ?? 'draft',
          });
        } else if (list.length > 0) {
          setForm((prev) => ({ ...prev, category_id: String(list[0].id) }));
        }
      } catch (err) {
        setError(extractError(err));
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  const applyInsert = (
    field: 'content' | 'content_ar',
    before: string,
    after: string,
    placeholder: string,
  ) => {
    const ref = field === 'content_ar' ? contentArRef : contentRef;
    const result = insertAroundSelection(ref.current, before, after, placeholder);
    if (!result) {
      setForm((prev) => ({
        ...prev,
        [field]: `${prev[field] || ''}${before}${placeholder}${after}`,
      }));
      return;
    }
    setForm((prev) => ({ ...prev, [field]: result.next }));
    requestAnimationFrame(() => {
      const el = ref.current;
      if (!el) return;
      el.focus();
      el.setSelectionRange(result.cursorStart, result.cursorEnd);
    });
  };

  const uploadInlineImage = async (file: File) => {
    const field = activeFieldRef.current === 'content_ar' ? 'content_ar' : 'content';
    setImageUploading(true);
    setError('');
    try {
      const { data } = await articleService.uploadImage(file);
      const alt = file.name.replace(/\.[^.]+$/, '') || 'image';
      applyInsert(field, `![${alt}](`, ')', data.url);
    } catch (err) {
      setError(extractError(err));
    } finally {
      setImageUploading(false);
    }
  };

  const uploadFeaturedImage = async (file: File) => {
    setImageUploading(true);
    setError('');
    try {
      const { data } = await articleService.uploadImage(file);
      setForm((prev) => ({ ...prev, featured_image_url: data.url }));
    } catch (err) {
      setError(extractError(err));
    } finally {
      setImageUploading(false);
      if (featuredInputRef.current) featuredInputRef.current.value = '';
    }
  };

  const uploadAttachment = async (file: File) => {
    setUploading(true);
    setError('');
    try {
      const { data } = await articleService.uploadAttachment(file);
      setForm((prev) => ({
        ...prev,
        attachment_url: data.attachment_url ?? data.url ?? '',
        attachment_name: data.attachment_name ?? data.name ?? '',
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

  const handleAttachmentChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadAttachment(file);
  };

  const removeAttachment = () => {
    setForm((prev) => ({ ...prev, attachment_url: '', attachment_name: '' }));
  };

  const handleSubmit = async (e: FormEvent) => {
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
        attachment_version: form.attachment_version,
        document_label: form.document_label,
        is_controlled_document: form.is_controlled_document,
        audio_media_id: form.audio_media_id || null,
        video_media_id: form.video_media_id || null,
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

  const previewHtml = renderMarkdown(previewLang === 'ar' ? form.content_ar : form.content);
  const statusLabel = {
    draft: t('articles.statusDraft'),
    pending_review: t('articles.statusPendingReview'),
    published: t('articles.statusPublished'),
    archived: t('articles.statusArchived'),
  }[form.status];

  return (
    <form onSubmit={handleSubmit}>
      <CmsEditorShell
        backTo="/articles/manage"
        backLabel={t('articles.manageTitle')}
        title={isEdit ? t('articles.editTitle') : t('articles.createTitle')}
        subtitle={isEdit ? t('articles.editSubtitle') : t('articles.createSubtitle')}
        status={form.status}
        statusLabel={statusLabel}
        error={error}
        sidebar={
          <>
            <CmsSidebarCard title={t('cms.publish')}>
              <label className="label">{t('articles.fieldStatus')}</label>
              <select
                className="input"
                value={form.status}
                onChange={(e) => setForm({ ...form, status: e.target.value })}
              >
                <option value="draft">{t('articles.statusDraft')}</option>
                <option value="pending_review">{t('articles.statusPendingReview')}</option>
                <option value="published">{t('articles.statusPublished')}</option>
                <option value="archived">{t('articles.statusArchived')}</option>
              </select>
              <label className="label mt-3">{t('articles.category')}</label>
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
              <label className="label mt-3">{t('articles.fieldTags')}</label>
              <input
                className="input"
                placeholder={t('articles.tagsPlaceholder')}
                value={form.tags}
                onChange={(e) => setForm({ ...form, tags: e.target.value })}
              />
            </CmsSidebarCard>
            <CmsSidebarCard title={t('cms.media')}>
              <label className="label">{t('articles.fieldImage')}</label>
              <p className="mb-2 text-xs text-ink-700/60 dark:text-slate-400">{t('articles.imageUploadHint')}</p>
              {form.featured_image_url && (
                <img
                  src={resolveMediaUrl(form.featured_image_url)}
                  alt=""
                  className="mb-3 h-32 w-full rounded-lg object-cover"
                />
              )}
              <input
                ref={featuredInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp,image/gif"
                className="input mb-2"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) uploadFeaturedImage(file);
                }}
                disabled={imageUploading}
              />
              <input
                className="input"
                type="url"
                placeholder={t('articles.fieldImageUrl')}
                value={form.featured_image_url}
                onChange={(e) => setForm({ ...form, featured_image_url: e.target.value })}
              />
              <label className="label mt-3">{t('articles.fieldAudio')}</label>
              <select
                className="input"
                value={form.audio_media_id}
                onChange={(e) => setForm({ ...form, audio_media_id: e.target.value })}
              >
                <option value="">{t('articles.mediaNone')}</option>
                {audioOptions.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.title}
                  </option>
                ))}
              </select>
              <label className="label mt-3">{t('articles.fieldVideo')}</label>
              <select
                className="input"
                value={form.video_media_id}
                onChange={(e) => setForm({ ...form, video_media_id: e.target.value })}
              >
                <option value="">{t('articles.mediaNone')}</option>
                {videoOptions.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.title}
                  </option>
                ))}
              </select>
            </CmsSidebarCard>
            <CmsSidebarCard title={t('articles.fieldAttachment')}>
              <p className="text-xs text-ink-700/60 dark:text-slate-400">{t('articles.attachmentHint')}</p>
              {form.attachment_url ? (
                <div className="space-y-2">
                  <a
                    href={resolveMediaUrl(form.attachment_url)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-sm font-medium text-brand-700 hover:underline dark:text-brand-400"
                  >
                    <FileText className="h-4 w-4 shrink-0" />
                    <span className="truncate">{form.attachment_name || form.attachment_url}</span>
                  </a>
                  <button type="button" className="btn-secondary w-full text-sm" onClick={removeAttachment}>
                    {t('articles.attachmentRemove')}
                  </button>
                </div>
              ) : (
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                  className="input"
                  onChange={handleAttachmentChange}
                  disabled={uploading}
                />
              )}
              {uploading && (
                <p className="text-xs text-ink-700/60 dark:text-slate-400">{t('articles.attachmentUploading')}</p>
              )}
              <label className="mt-2 flex items-center gap-2 text-sm text-ink-700 dark:text-slate-300">
                <input
                  type="checkbox"
                  checked={form.is_controlled_document}
                  onChange={(e) => setForm({ ...form, is_controlled_document: e.target.checked })}
                />
                {t('articles.controlledDocument')}
              </label>
              {form.is_controlled_document && (
                <div className="space-y-3">
                  <div>
                    <label className="label">{t('articles.documentLabel')}</label>
                    <input
                      className="input"
                      value={form.document_label}
                      onChange={(e) => setForm({ ...form, document_label: e.target.value })}
                      placeholder={t('articles.documentLabelPlaceholder')}
                      required={form.is_controlled_document}
                    />
                  </div>
                  <div>
                    <label className="label">{t('articles.attachmentVersion')}</label>
                    <input
                      className="input"
                      value={form.attachment_version}
                      onChange={(e) => setForm({ ...form, attachment_version: e.target.value })}
                      placeholder="v2021.1"
                      required={form.is_controlled_document}
                    />
                  </div>
                </div>
              )}
            </CmsSidebarCard>
          </>
        }
        footer={
          <>
            <button type="submit" className="btn-primary" disabled={saving || uploading || imageUploading}>
              {saving ? t('common.loading') : t('common.save')}
            </button>
            <Link to="/articles/manage" className="btn-secondary">
              {t('common.cancel')}
            </Link>
          </>
        }
      >
        <div className="card space-y-4">
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
            <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
              <label className="label mb-0">{t('articles.fieldContent')}</label>
              <div className="flex items-center gap-3">
                {showPreview && (
                  <select
                    className="input py-1 text-sm"
                    value={previewLang}
                    onChange={(e) => setPreviewLang(e.target.value)}
                  >
                    <option value="en">EN</option>
                    <option value="ar">AR</option>
                  </select>
                )}
                <button
                  type="button"
                  className="text-sm text-brand-600 hover:underline dark:text-brand-400"
                  onClick={() => setShowPreview((v) => !v)}
                >
                  {showPreview ? t('articles.hidePreview') : t('articles.showPreview')}
                </button>
              </div>
            </div>
            <p className="mb-2 text-xs text-ink-700/60 dark:text-slate-400">{t('articles.markdownHint')}</p>
            {!showPreview ? (
              <>
                <MarkdownToolbar
                  uploading={imageUploading}
                  onInsert={(before: string, after: string, placeholder: string) => {
                    activeFieldRef.current = 'content';
                    applyInsert('content', before, after, placeholder);
                  }}
                  onUploadImage={(file: File) => {
                    activeFieldRef.current = 'content';
                    uploadInlineImage(file);
                  }}
                />
                <textarea
                  ref={contentRef}
                  className="input min-h-[220px] font-mono text-sm"
                  value={form.content}
                  onFocus={() => {
                    activeFieldRef.current = 'content';
                  }}
                  onChange={(e) => setForm({ ...form, content: e.target.value })}
                  required
                />
              </>
            ) : (
              <div
                className="prose min-h-[220px] max-w-none rounded-lg border border-ink-100 bg-ink-50 p-4 dark:border-slate-600 dark:bg-slate-900 dark:prose-invert"
                dangerouslySetInnerHTML={{ __html: previewHtml }}
              />
            )}
          </div>
          <div>
            <label className="label">{t('articles.fieldContentAr')}</label>
            {!showPreview && (
              <MarkdownToolbar
                uploading={imageUploading}
                onInsert={(before: string, after: string, placeholder: string) => {
                  activeFieldRef.current = 'content_ar';
                  applyInsert('content_ar', before, after, placeholder);
                }}
                onUploadImage={(file: File) => {
                  activeFieldRef.current = 'content_ar';
                  uploadInlineImage(file);
                }}
              />
            )}
            <textarea
              ref={contentArRef}
              className="input min-h-[160px] font-mono text-sm"
              dir="rtl"
              value={form.content_ar}
              onFocus={() => {
                activeFieldRef.current = 'content_ar';
              }}
              onChange={(e) => setForm({ ...form, content_ar: e.target.value })}
            />
          </div>
        </div>
      </CmsEditorShell>
    </form>
  );
}
