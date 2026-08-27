import { useEffect, useState, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Spinner } from '../components/ui';
import { CmsEditorShell, CmsSidebarCard } from '../components/CmsWorkspace';
import { extractError } from '../lib/api';
import { categoryService, mediaService } from '../lib/services';

const emptyForm = {
  title: '',
  title_ar: '',
  description: '',
  description_ar: '',
  media_type: 'audio',
  source: 'external',
  file_url: '',
  external_url: '',
  mime_type: '',
  thumbnail_url: '',
  captions_url: '',
  category_id: '',
  status: 'draft',
};

export function MediaEditorPage() {
  const { t } = useTranslation();
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const [form, setForm] = useState(emptyForm);
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    categoryService.list().then(({ data }) => {
      setCategories(data.results ?? data ?? []);
    });
  }, []);

  useEffect(() => {
    if (!isEdit) return undefined;
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const { data } = await mediaService.get(id);
        if (cancelled) return;
        setForm({
          title: data.title ?? '',
          title_ar: data.title_ar ?? '',
          description: data.description ?? '',
          description_ar: data.description_ar ?? '',
          media_type: data.media_type ?? 'audio',
          source: data.source ?? 'external',
          file_url: data.file_url ?? '',
          external_url: data.external_url ?? '',
          mime_type: data.mime_type ?? '',
          thumbnail_url: data.thumbnail_url ?? '',
          captions_url: data.captions_url ?? '',
          category_id: data.category?.id ?? '',
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

  const uploadFile = async (file: File) => {
    setUploading(true);
    setError('');
    try {
      const { data } =
        form.media_type === 'audio'
          ? await mediaService.uploadAudio(file)
          : await mediaService.uploadVideo(file);
      setForm((prev) => ({
        ...prev,
        source: 'upload',
        file_url: data.url,
        mime_type: data.mime_type || prev.mime_type,
        external_url: '',
      }));
    } catch (err) {
      setError(extractError(err));
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const payload = {
        title: form.title,
        title_ar: form.title_ar,
        description: form.description,
        description_ar: form.description_ar,
        media_type: form.media_type,
        source: form.source,
        file_url: form.source === 'upload' ? form.file_url : '',
        external_url: form.source === 'external' ? form.external_url : '',
        mime_type: form.mime_type,
        thumbnail_url: form.thumbnail_url,
        category_id: form.category_id || null,
        status: form.status,
      };
      if (isEdit) {
        await mediaService.update(id, payload);
      } else {
        await mediaService.create(payload);
      }
      navigate('/media/manage');
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
        backTo="/media/manage"
        backLabel={t('media.manageTitle')}
        title={isEdit ? t('media.editTitle') : t('media.createTitle')}
        subtitle={isEdit ? t('media.editSubtitle') : t('media.createSubtitle')}
        status={form.status}
        statusLabel={form.status === 'published' ? t('media.statusPublished') : form.status === 'archived' ? t('media.statusArchived') : t('media.statusDraft')}
        error={error}
        sidebar={
          <CmsSidebarCard title={t('cms.publish')}>
            <label className="label">{t('media.fieldType')}</label>
            <select
              className="input"
              value={form.media_type}
              onChange={(e) => setForm({ ...form, media_type: e.target.value })}
              disabled={isEdit}
            >
              <option value="audio">{t('media.typeAudio')}</option>
              <option value="video">{t('media.typeVideo')}</option>
            </select>
            <label className="label mt-3">{t('media.fieldStatus')}</label>
            <select
              className="input"
              value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value })}
            >
              <option value="draft">{t('media.statusDraft')}</option>
              <option value="published">{t('media.statusPublished')}</option>
              <option value="archived">{t('media.statusArchived')}</option>
            </select>
            <label className="label mt-3">{t('media.fieldSource')}</label>
            <select
              className="input"
              value={form.source}
              onChange={(e) => setForm({ ...form, source: e.target.value })}
            >
              <option value="external">{t('media.sourceExternal')}</option>
              <option value="upload">{t('media.sourceUpload')}</option>
            </select>
            <label className="label mt-3">{t('media.fieldCategory')}</label>
            <select
              className="input"
              value={form.category_id}
              onChange={(e) => setForm({ ...form, category_id: e.target.value })}
            >
              <option value="">{t('common.all')}</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </CmsSidebarCard>
        }
        footer={
          <>
            <button type="submit" className="btn-primary" disabled={saving || uploading}>
              {saving ? t('common.loading') : t('common.save')}
            </button>
            <Link to="/media/manage" className="btn-secondary">
              {t('common.cancel')}
            </Link>
          </>
        }
      >
        <div className="card space-y-4">
          <div>
            <label className="label">{t('media.fieldTitle')}</label>
            <input
              className="input"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="label">{t('media.fieldTitleAr')}</label>
            <input
              className="input"
              value={form.title_ar}
              onChange={(e) => setForm({ ...form, title_ar: e.target.value })}
            />
          </div>
          <div>
            <label className="label">{t('media.fieldDescription')}</label>
            <textarea
              className="input min-h-[80px]"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>
          <div>
            <label className="label">{t('media.fieldDescriptionAr')}</label>
            <textarea
              className="input min-h-[80px]"
              value={form.description_ar}
              onChange={(e) => setForm({ ...form, description_ar: e.target.value })}
            />
          </div>
          {form.source === 'external' ? (
            <div>
              <label className="label">{t('media.fieldExternalUrl')}</label>
              <input
                className="input"
                type="url"
                value={form.external_url}
                onChange={(e) => setForm({ ...form, external_url: e.target.value })}
                placeholder="https://"
                required
              />
              <p className="mt-1 text-xs text-ink-700/60 dark:text-slate-400">
                {t('media.externalHint')}
              </p>
            </div>
          ) : (
            <div>
              <label className="label">{t('media.fieldUpload')}</label>
              <input
                type="file"
                accept={
                  form.media_type === 'audio'
                    ? 'audio/mpeg,audio/mp4,audio/ogg,audio/wav,.mp3,.m4a,.ogg,.wav'
                    : 'video/mp4,video/webm,.mp4,.webm'
                }
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) uploadFile(file);
                }}
              />
              {uploading && (
                <p className="mt-1 text-xs text-ink-700/60">{t('media.uploading')}</p>
              )}
              {form.file_url && (
                <p className="mt-2 truncate text-xs text-brand-700 dark:text-brand-400">
                  {form.file_url}
                </p>
              )}
            </div>
          )}
          <div>
            <label className="label">{t('media.fieldCaptions')}</label>
            <input
              className="input"
              type="url"
              value={form.captions_url}
              onChange={(e) => setForm({ ...form, captions_url: e.target.value })}
              placeholder="https:// (WebVTT .vtt)"
            />
            <p className="mt-1 text-xs text-ink-700/60 dark:text-slate-400">{t('media.captionsHint')}</p>
          </div>
          <div>
            <label className="label">{t('media.fieldThumbnail')}</label>
            <input
              className="input"
              type="url"
              value={form.thumbnail_url}
              onChange={(e) => setForm({ ...form, thumbnail_url: e.target.value })}
              placeholder="https://"
            />
          </div>
        </div>
      </CmsEditorShell>
    </form>
  );
}
