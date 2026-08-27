// @ts-nocheck
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useOrganization } from '../context/OrganizationContext';
import { Alert, ConfirmDialog, EmptyState, Spinner } from '../components/ui';
import { CmsManageHeader } from '../components/CmsWorkspace';
import { ChevronLeft } from '../components/Icons';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { categoryService } from '../lib/services';

function slugify(value) {
  return value
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '');
}

const EMPTY_FORM = {
  name: '',
  slug: '',
  description: '',
  name_ar: '',
  description_ar: '',
  is_locked: false,
};

export function CategoriesManagePage() {
  const { t } = useTranslation();
  const { isOrgAdmin } = useOrganization();
  const [form, setForm] = useState(EMPTY_FORM);
  const [editId, setEditId] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);
  const [pendingDelete, setPendingDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const { data, isLoading, error: loadError, refetch } = useQuery({
    queryKey: queryKeys.categoriesManage,
    queryFn: async () => {
      const { data: res } = await categoryService.list();
      return res.results ?? res;
    },
    enabled: isOrgAdmin,
  });

  const resetForm = () => {
    setForm(EMPTY_FORM);
    setEditId(null);
  };

  const startEdit = (cat) => {
    setEditId(cat.id);
    setForm({
      name: cat.name ?? '',
      slug: cat.slug ?? '',
      description: cat.description ?? '',
      name_ar: cat.name_ar ?? '',
      description_ar: cat.description_ar ?? '',
      is_locked: Boolean(cat.is_locked),
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const payload = {
        ...form,
        slug: form.slug || slugify(form.name),
      };
      if (editId) {
        await categoryService.update(editId, payload);
        setSuccess(t('categories.updated'));
      } else {
        await categoryService.create(payload);
        setSuccess(t('categories.created'));
      }
      resetForm();
      await refetch();
    } catch (err) {
      setError(extractError(err));
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setDeleting(true);
    setError('');
    try {
      await categoryService.remove(pendingDelete.id);
      setPendingDelete(null);
      await refetch();
    } catch (err) {
      setError(extractError(err));
    } finally {
      setDeleting(false);
    }
  };

  if (!isOrgAdmin) {
    return (
      <div>
        <CmsManageHeader title={t('categories.manageTitle')} />
        <Alert>{t('categories.adminOnly')}</Alert>
      </div>
    );
  }

  if (isLoading) return <Spinner />;

  const categories = data ?? [];

  return (
    <div className="mx-auto max-w-3xl">
      <CmsManageHeader title={t('categories.manageTitle')} subtitle={t('categories.manageSubtitle')} />
      <Link to="/articles/manage" className="mb-4 inline-flex items-center gap-1 text-sm text-brand-600 hover:underline dark:text-brand-400">
        <ChevronLeft className="h-4 w-4" />
        {t('articles.manageTitle')}
      </Link>

      {error && (
        <div className="mb-4">
          <Alert>{error}</Alert>
        </div>
      )}
      {success && (
        <div className="mb-4">
          <Alert kind="success">{success}</Alert>
        </div>
      )}
      {loadError && (
        <div className="mb-4">
          <Alert>{extractError(loadError)}</Alert>
        </div>
      )}

      <form onSubmit={handleSubmit} className="card mb-8 space-y-4">
        <h2 className="text-lg font-semibold">
          {editId ? t('categories.editTitle') : t('categories.createTitle')}
        </h2>
        <div>
          <label className="label">{t('categories.fieldName')}</label>
          <input
            className="input"
            value={form.name}
            onChange={(e) =>
              setForm({
                ...form,
                name: e.target.value,
                slug: editId ? form.slug : slugify(e.target.value),
              })
            }
            required
          />
        </div>
        <div>
          <label className="label">{t('categories.fieldSlug')}</label>
          <input
            className="input"
            value={form.slug}
            onChange={(e) => setForm({ ...form, slug: e.target.value })}
            required
          />
        </div>
        <div>
          <label className="label">{t('categories.fieldNameAr')}</label>
          <input
            className="input"
            value={form.name_ar}
            onChange={(e) => setForm({ ...form, name_ar: e.target.value })}
          />
        </div>
        <div>
          <label className="label">{t('categories.fieldDescription')}</label>
          <textarea
            className="input min-h-[60px]"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </div>
        <label className="flex items-center gap-2 text-sm text-ink-700 dark:text-slate-300">
          <input
            type="checkbox"
            checked={form.is_locked}
            onChange={(e) => setForm({ ...form, is_locked: e.target.checked })}
          />
          {t('categories.lockCurriculum')}
        </label>
        <p className="text-xs text-ink-700/60 dark:text-slate-400">{t('categories.lockHint')}</p>
        <div className="flex flex-wrap gap-3">
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? t('common.loading') : editId ? t('common.save') : t('common.create')}
          </button>
          {editId && (
            <button type="button" className="btn-secondary" onClick={resetForm}>
              {t('common.cancel')}
            </button>
          )}
        </div>
      </form>

      {categories.length === 0 ? (
        <EmptyState>{t('categories.empty')}</EmptyState>
      ) : (
        <ul className="divide-y divide-ink-100 rounded-xl border border-ink-100 bg-white dark:divide-slate-700 dark:border-slate-700 dark:bg-slate-800">
          {categories.map((cat) => (
            <li key={cat.id} className="flex items-center justify-between gap-4 px-4 py-3">
              <div>
                <p className="font-medium text-ink-900 dark:text-slate-100">
                  {cat.name}
                  {cat.is_locked ? (
                    <span className="ml-2 text-xs font-normal text-amber-700 dark:text-amber-300">
                      ({t('categories.locked')})
                    </span>
                  ) : null}
                </p>
                <p className="text-xs text-ink-700/60 dark:text-slate-400">{cat.slug}</p>
              </div>
              <div className="flex gap-2">
                <button type="button" className="btn-secondary text-xs" onClick={() => startEdit(cat)}>
                  {t('common.edit')}
                </button>
                {!cat.is_locked && (
                  <button
                    type="button"
                    className="btn-danger text-xs"
                    onClick={() => setPendingDelete({ id: cat.id, name: cat.name })}
                  >
                    {t('common.delete')}
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}

      <ConfirmDialog
        open={!!pendingDelete}
        title={t('common.confirmDelete')}
        message={pendingDelete ? t('categories.deleteConfirm', { name: pendingDelete.name }) : ''}
        confirmLabel={t('common.delete')}
        onConfirm={confirmDelete}
        onCancel={() => {
          if (deleting) return;
          setPendingDelete(null);
        }}
        busy={deleting}
      />
    </div>
  );
}
