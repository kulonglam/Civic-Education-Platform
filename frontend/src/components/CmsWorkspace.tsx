// @ts-nocheck
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Alert, PageHeader } from './ui';
import { ChevronLeft } from './Icons';

const STATUS_TONES = {
  draft: 'bg-ink-100 text-ink-800 dark:bg-slate-700 dark:text-slate-100',
  published: 'bg-green-100 text-green-800 dark:bg-green-950/50 dark:text-green-300',
  pending_review: 'bg-amber-100 text-amber-900 dark:bg-amber-950/50 dark:text-amber-200',
  archived: 'bg-slate-200 text-slate-800 dark:bg-slate-700 dark:text-slate-200',
  cancelled: 'bg-red-100 text-red-800 dark:bg-red-950/40 dark:text-red-300',
  open: 'bg-green-100 text-green-800 dark:bg-green-950/50 dark:text-green-300',
  closed: 'bg-slate-200 text-slate-800 dark:bg-slate-700 dark:text-slate-200',
  active: 'bg-green-100 text-green-800 dark:bg-green-950/50 dark:text-green-300',
};

export function StatusBadge({ status, label }) {
  const tone = STATUS_TONES[status] || STATUS_TONES.draft;
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${tone}`}>
      {label || String(status || '').replace(/_/g, ' ')}
    </span>
  );
}

export function CmsManageHeader({ title, subtitle, primaryTo, primaryLabel, secondary }) {
  const { t } = useTranslation();
  return (
    <PageHeader
      eyebrow={t('cms.workspace')}
      title={title}
      subtitle={subtitle}
      action={
        <div className="flex flex-wrap items-center gap-2">
          {secondary}
          {primaryTo && (
            <Link to={primaryTo} className="btn-primary">
              {primaryLabel}
            </Link>
          )}
        </div>
      }
    />
  );
}

export function CmsEditorShell({
  backTo,
  backLabel,
  title,
  subtitle,
  status,
  statusLabel,
  error,
  sidebar,
  footer,
  children,
}) {
  const { t } = useTranslation();
  return (
    <div className="cms-editor">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          {backTo && (
            <Link
              to={backTo}
              className="mb-2 inline-flex items-center gap-1 text-sm font-medium text-brand-700 hover:underline dark:text-brand-400"
            >
              <ChevronLeft className="h-4 w-4" />
              {backLabel || t('common.back')}
            </Link>
          )}
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="font-display text-page-title text-ink-900 dark:text-slate-50">{title}</h1>
            {status ? <StatusBadge status={status} label={statusLabel} /> : null}
          </div>
          {subtitle && (
            <p className="mt-2 max-w-2xl text-sm text-ink-700/70 dark:text-slate-400">{subtitle}</p>
          )}
        </div>
      </div>
      {error && (
        <div className="mb-4">
          <Alert>{error}</Alert>
        </div>
      )}
      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_18rem]">
        <div className="min-w-0 space-y-4">{children}</div>
        {sidebar ? (
          <aside className="cms-editor-sidebar space-y-4 lg:sticky lg:top-24">{sidebar}</aside>
        ) : null}
      </div>
      {footer ? (
        <div className="cms-editor-footer mt-6 flex flex-wrap items-center gap-3 border-t border-ink-100 pt-4 dark:border-slate-700">
          {footer}
        </div>
      ) : null}
    </div>
  );
}

export function CmsSidebarCard({ title, children }) {
  return (
    <div className="card space-y-3">
      {title && <h2 className="text-sm font-semibold text-ink-900 dark:text-slate-100">{title}</h2>}
      {children}
    </div>
  );
}
