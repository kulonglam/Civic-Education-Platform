// @ts-nocheck
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import { Spinner } from '../components/ui';
import { CmsEditorShell, CmsSidebarCard } from '../components/CmsWorkspace';
import { extractError } from '../lib/api';
import { engagementService } from '../lib/services';

const emptyPoll = {
  question: '',
  question_ar: '',
  description: '',
  description_ar: '',
  kind: 'community',
  status: 'draft',
  options: [
    { label: '', label_ar: '' },
    { label: '', label_ar: '' },
  ],
};

const emptyPetition = {
  title: '',
  title_ar: '',
  description: '',
  description_ar: '',
  goal_signatures: 100,
  status: 'draft',
};

const emptyCampaign = {
  title: '',
  title_ar: '',
  description: '',
  description_ar: '',
  link_url: '',
  status: 'draft',
};

export function EngagementEditorPage() {
  const { t } = useTranslation();
  const { kind, id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const [form, setForm] = useState(
    kind === 'polls' ? emptyPoll : kind === 'petitions' ? emptyPetition : emptyCampaign,
  );
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isEdit) {
      setForm(kind === 'polls' ? emptyPoll : kind === 'petitions' ? emptyPetition : emptyCampaign);
      return undefined;
    }
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const loader =
          kind === 'polls'
            ? engagementService.getPoll
            : kind === 'petitions'
              ? engagementService.getPetition
              : engagementService.getCampaign;
        const { data } = await loader(id);
        if (cancelled) return;
        if (kind === 'polls') {
          setForm({
            question: data.question ?? '',
            question_ar: data.question_ar ?? '',
            description: data.description ?? '',
            description_ar: data.description_ar ?? '',
            kind: data.kind ?? 'community',
            status: data.status ?? 'draft',
            options: (data.options || []).map((opt) => ({
              id: opt.id,
              label: opt.label ?? '',
              label_ar: opt.label_ar ?? '',
            })),
          });
        } else if (kind === 'petitions') {
          setForm({
            title: data.title ?? '',
            title_ar: data.title_ar ?? '',
            description: data.description ?? '',
            description_ar: data.description_ar ?? '',
            goal_signatures: data.goal_signatures ?? 100,
            status: data.status ?? 'draft',
          });
        } else {
          setForm({
            title: data.title ?? '',
            title_ar: data.title_ar ?? '',
            description: data.description ?? '',
            description_ar: data.description_ar ?? '',
            link_url: data.link_url ?? '',
            status: data.status ?? 'draft',
          });
        }
      } catch (err) {
        if (!cancelled) setError(extractError(err));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [id, isEdit, kind]);

  const setField = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      if (kind === 'polls') {
        const payload = { ...form, options: form.options.filter((opt) => opt.label.trim()) };
        if (isEdit) await engagementService.updatePoll(id, payload);
        else await engagementService.createPoll(payload);
      } else if (kind === 'petitions') {
        if (isEdit) await engagementService.updatePetition(id, form);
        else await engagementService.createPetition(form);
      } else if (isEdit) {
        await engagementService.updateCampaign(id, form);
      } else {
        await engagementService.createCampaign(form);
      }
      navigate('/engage/manage');
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
        backTo="/engage/manage"
        backLabel={t('engage.manageTitle')}
        title={isEdit ? t(`engage.edit_${kind}`) : t(`engage.create_${kind}`)}
        subtitle={t('engage.editorHint')}
        status={form.status}
        statusLabel={t(`engage.status.${form.status}`)}
        error={error}
        sidebar={
          <CmsSidebarCard title={t('cms.publish')}>
            <p className="text-sm text-ink-700/70 dark:text-slate-400">{t('engage.editorHint')}</p>
          </CmsSidebarCard>
        }
        footer={
          <>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? t('common.loading') : t('common.save')}
            </button>
            <button type="button" className="btn-secondary" onClick={() => navigate('/engage/manage')}>
              {t('common.cancel')}
            </button>
          </>
        }
      >
        <div className="card space-y-4">
        {kind === 'polls' ? (
          <>
            <label className="grid gap-1 text-sm font-medium">
              {t('engage.fields.question')}
              <input className="input" required value={form.question} onChange={(e) => setField('question', e.target.value)} />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              {t('engage.fields.questionAr')}
              <input className="input" value={form.question_ar} onChange={(e) => setField('question_ar', e.target.value)} />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              {t('engage.fields.description')}
              <textarea className="input min-h-[6rem]" value={form.description} onChange={(e) => setField('description', e.target.value)} />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              {t('engage.fields.descriptionAr')}
              <textarea className="input min-h-[6rem]" value={form.description_ar} onChange={(e) => setField('description_ar', e.target.value)} />
            </label>
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="grid gap-1 text-sm font-medium">
                {t('engage.pollKind')}
                <select className="input" value={form.kind} onChange={(e) => setField('kind', e.target.value)}>
                  <option value="community">{t('engage.kind_community')}</option>
                  <option value="educational">{t('engage.kind_educational')}</option>
                </select>
              </label>
              <label className="grid gap-1 text-sm font-medium">
                {t('engage.fields.status')}
                <select className="input" value={form.status} onChange={(e) => setField('status', e.target.value)}>
                  <option value="draft">{t('engage.status.draft')}</option>
                  <option value="open">{t('engage.status.open')}</option>
                  <option value="closed">{t('engage.status.closed')}</option>
                </select>
              </label>
            </div>
            <fieldset className="grid gap-3">
              <legend className="text-sm font-medium">{t('engage.fields.options')}</legend>
              {form.options.map((opt, index) => (
                <div key={opt.id || index} className="grid gap-2 sm:grid-cols-2">
                  <input
                    className="input"
                    required
                    placeholder={t('engage.fields.optionEn')}
                    value={opt.label}
                    onChange={(e) => {
                      const next = [...form.options];
                      next[index] = { ...next[index], label: e.target.value };
                      setField('options', next);
                    }}
                  />
                  <input
                    className="input"
                    placeholder={t('engage.fields.optionAr')}
                    value={opt.label_ar}
                    onChange={(e) => {
                      const next = [...form.options];
                      next[index] = { ...next[index], label_ar: e.target.value };
                      setField('options', next);
                    }}
                  />
                </div>
              ))}
              {form.options.length < 8 && (
                <button
                  type="button"
                  className="btn-secondary justify-self-start text-sm"
                  onClick={() => setField('options', [...form.options, { label: '', label_ar: '' }])}
                >
                  {t('engage.addOption')}
                </button>
              )}
            </fieldset>
          </>
        ) : (
          <>
            <label className="grid gap-1 text-sm font-medium">
              {t('engage.fields.title')}
              <input className="input" required value={form.title} onChange={(e) => setField('title', e.target.value)} />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              {t('engage.fields.titleAr')}
              <input className="input" value={form.title_ar} onChange={(e) => setField('title_ar', e.target.value)} />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              {t('engage.fields.description')}
              <textarea className="input min-h-[8rem]" required value={form.description} onChange={(e) => setField('description', e.target.value)} />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              {t('engage.fields.descriptionAr')}
              <textarea className="input min-h-[6rem]" value={form.description_ar} onChange={(e) => setField('description_ar', e.target.value)} />
            </label>
            {kind === 'petitions' && (
              <label className="grid gap-1 text-sm font-medium">
                {t('engage.fields.goal')}
                <input
                  className="input"
                  type="number"
                  min={1}
                  value={form.goal_signatures}
                  onChange={(e) => setField('goal_signatures', Number(e.target.value) || 1)}
                />
              </label>
            )}
            {kind === 'campaigns' && (
              <label className="grid gap-1 text-sm font-medium">
                {t('engage.fields.link')}
                <input className="input" type="url" value={form.link_url} onChange={(e) => setField('link_url', e.target.value)} />
              </label>
            )}
            <label className="grid gap-1 text-sm font-medium">
              {t('engage.fields.status')}
              <select className="input" value={form.status} onChange={(e) => setField('status', e.target.value)}>
                <option value="draft">{t('engage.status.draft')}</option>
                {kind === 'campaigns' ? (
                  <>
                    <option value="active">{t('engage.status.active')}</option>
                    <option value="archived">{t('engage.status.archived')}</option>
                  </>
                ) : (
                  <>
                    <option value="open">{t('engage.status.open')}</option>
                    <option value="closed">{t('engage.status.closed')}</option>
                  </>
                )}
              </select>
            </label>
          </>
        )}
        </div>
      </CmsEditorShell>
    </form>
  );
}
