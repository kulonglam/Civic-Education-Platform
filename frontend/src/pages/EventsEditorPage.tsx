// @ts-nocheck
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { EVENT_KINDS } from '../components/EventKindBadge';
import { Spinner } from '../components/ui';
import { CmsEditorShell } from '../components/CmsWorkspace';
import { extractError } from '../lib/api';
import { eventsService } from '../lib/services';
import { REGION_OPTIONS } from '../lib/demographics';

const emptyForm = {
  title: '',
  title_ar: '',
  description: '',
  description_ar: '',
  location: '',
  location_ar: '',
  kind: 'community_meeting',
  starts_at: '',
  ends_at: '',
  is_all_day: false,
  allows_registration: true,
  capacity: '',
  source_name: '',
  source_url: '',
  status: 'draft',
  region: '',
};

function pad(value) {
  return String(value).padStart(2, '0');
}

function toDateTimeLocal(iso) {
  if (!iso) return '';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '';
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function toDateInput(iso) {
  if (!iso) return '';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '';
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

function fromDateTimeLocal(value) {
  if (!value) return null;
  return new Date(value).toISOString();
}

function fromDateInput(value, endOfDay = false) {
  if (!value) return null;
  return new Date(`${value}${endOfDay ? 'T23:59:00' : 'T00:00:00'}`).toISOString();
}

export function EventsEditorPage() {
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
        const { data } = await eventsService.get(id);
        if (cancelled) return;
        setForm({
          title: data.title ?? '',
          title_ar: data.title_ar ?? '',
          description: data.description ?? '',
          description_ar: data.description_ar ?? '',
          location: data.location ?? '',
          location_ar: data.location_ar ?? '',
          kind: data.kind ?? 'community_meeting',
          starts_at: data.is_all_day ? toDateInput(data.starts_at) : toDateTimeLocal(data.starts_at),
          ends_at: data.is_all_day ? toDateInput(data.ends_at) : toDateTimeLocal(data.ends_at),
          is_all_day: Boolean(data.is_all_day),
          allows_registration: data.kind === 'national_holiday' ? false : Boolean(data.allows_registration),
          capacity: data.capacity ?? '',
          source_name: data.source_name ?? '',
          source_url: data.source_url ?? '',
          status: data.status ?? 'draft',
          region: data.region ?? '',
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
    setForm((prev) => {
      const next = { ...prev, [key]: value };
      if (key === 'kind' && value === 'national_holiday') {
        next.is_all_day = true;
        next.allows_registration = false;
        next.starts_at = toDateInput(fromDateTimeLocal(prev.starts_at) || prev.starts_at);
        next.ends_at = toDateInput(fromDateTimeLocal(prev.ends_at) || prev.ends_at);
      }
      return next;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const payload = {
        ...form,
        starts_at: form.is_all_day ? fromDateInput(form.starts_at) : fromDateTimeLocal(form.starts_at),
        ends_at: form.is_all_day ? fromDateInput(form.ends_at, true) : fromDateTimeLocal(form.ends_at),
        capacity: form.capacity === '' ? null : Number(form.capacity),
        allows_registration: form.kind === 'national_holiday' ? false : form.allows_registration,
      };
      if (isEdit) {
        await eventsService.update(id, payload);
        navigate(`/events/${id}`);
      } else {
        const { data } = await eventsService.create(payload);
        navigate(`/events/${data.id}`);
      }
    } catch (err) {
      setError(extractError(err));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Spinner />;

  const holiday = form.kind === 'national_holiday';

  return (
    <form onSubmit={handleSubmit}>
      <CmsEditorShell
        backTo="/events/manage"
        backLabel={t('events.manageTitle')}
        title={isEdit ? t('events.editTitle') : t('events.create')}
        subtitle={t('events.editorHint')}
        status={form.status}
        statusLabel={t(`events.status.${form.status}`)}
        error={error}
        footer={
          <>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? t('common.loading') : t('common.save')}
            </button>
            <Link to="/events/manage" className="btn-secondary">
              {t('common.cancel')}
            </Link>
          </>
        }
      >
        <div className="card grid gap-4">
        <label className="grid gap-1 text-sm font-medium">
          {t('events.fields.title')}
          <input className="input" required value={form.title} onChange={(e) => setField('title', e.target.value)} />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('events.fields.titleAr')}
          <input className="input" value={form.title_ar} onChange={(e) => setField('title_ar', e.target.value)} />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('events.fields.description')}
          <textarea
            className="input min-h-[10rem]"
            required
            value={form.description}
            onChange={(e) => setField('description', e.target.value)}
          />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('events.fields.descriptionAr')}
          <textarea
            className="input min-h-[8rem]"
            value={form.description_ar}
            onChange={(e) => setField('description_ar', e.target.value)}
          />
        </label>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="grid gap-1 text-sm font-medium">
            {t('events.fields.location')}
            <input className="input" value={form.location} onChange={(e) => setField('location', e.target.value)} />
          </label>
          <label className="grid gap-1 text-sm font-medium">
            {t('events.fields.locationAr')}
            <input className="input" value={form.location_ar} onChange={(e) => setField('location_ar', e.target.value)} />
          </label>
        </div>
        <label className="grid gap-1 text-sm font-medium">
          {t('events.fields.region')}
          <select className="input sm:max-w-xs" value={form.region} onChange={(e) => setField('region', e.target.value)}>
            <option value="">{t('events.fields.regionNationwide')}</option>
            {REGION_OPTIONS.filter((option) => option.value && option.value !== 'prefer_not').map((option) => (
              <option key={option.value} value={option.value}>
                {t(option.labelKey)}
              </option>
            ))}
          </select>
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('events.fields.kind')}
          <select className="input sm:max-w-xs" value={form.kind} onChange={(e) => setField('kind', e.target.value)}>
            {EVENT_KINDS.map((value) => (
              <option key={value} value={value}>
                {t(`events.kinds.${value}`)}
              </option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-2 text-sm font-medium">
          <input
            type="checkbox"
            checked={form.is_all_day}
            disabled={holiday}
            onChange={(e) => setField('is_all_day', e.target.checked)}
          />
          {t('events.fields.allDay')}
        </label>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="grid gap-1 text-sm font-medium">
            {t('events.fields.startsAt')}
            <input
              className="input"
              required
              type={form.is_all_day ? 'date' : 'datetime-local'}
              value={form.starts_at}
              onChange={(e) => setField('starts_at', e.target.value)}
            />
          </label>
          <label className="grid gap-1 text-sm font-medium">
            {t('events.fields.endsAt')}
            <input
              className="input"
              type={form.is_all_day ? 'date' : 'datetime-local'}
              value={form.ends_at}
              onChange={(e) => setField('ends_at', e.target.value)}
            />
          </label>
        </div>
        <label className="flex items-center gap-2 text-sm font-medium">
          <input
            type="checkbox"
            checked={form.allows_registration}
            disabled={holiday}
            onChange={(e) => setField('allows_registration', e.target.checked)}
          />
          {t('events.fields.allowsRegistration')}
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('events.fields.capacity')}
          <input
            className="input sm:max-w-xs"
            type="number"
            min="1"
            value={form.capacity}
            onChange={(e) => setField('capacity', e.target.value)}
          />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('events.fields.sourceName')}
          <input className="input" value={form.source_name} onChange={(e) => setField('source_name', e.target.value)} />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('events.fields.sourceUrl')}
          <input className="input" type="url" value={form.source_url} onChange={(e) => setField('source_url', e.target.value)} />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          {t('events.fields.status')}
          <select className="input sm:max-w-xs" value={form.status} onChange={(e) => setField('status', e.target.value)}>
            <option value="draft">{t('events.status.draft')}</option>
            <option value="published">{t('events.status.published')}</option>
            <option value="cancelled">{t('events.status.cancelled')}</option>
          </select>
        </label>
        </div>
      </CmsEditorShell>
    </form>
  );
}
