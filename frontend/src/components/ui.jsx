import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Eye, EyeOff } from "./Icons";
function Spinner({
  label,
  className = "",
}) {
  const {
    t
  } = useTranslation();
  return <div className={`flex items-center justify-center gap-3 py-12 text-ink-700/60 dark:text-slate-400 ${className}`.trim()} role="status"><span className="h-5 w-5 animate-spin rounded-full border-2 border-brand-600 border-t-transparent" aria-hidden="true" /><span className="text-sm font-medium">{label ?? t("common.loading")}</span></div>;
}
function Alert({
  kind = "error",
  children
}) {
  const styles = {
    error: "bg-red-50 text-red-700 border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-900",
    success: "bg-green-50 text-green-700 border-green-200 dark:bg-green-950/40 dark:text-green-300 dark:border-green-900",
    info: "bg-brand-50 text-brand-700 border-brand-200 dark:bg-brand-950/40 dark:text-brand-300 dark:border-brand-900",
    warning: "bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900"
  }[kind];
  return <div className={`rounded-xl border px-4 py-3.5 text-sm leading-relaxed shadow-soft ${styles}`}>{children}</div>;
}
function EmptyState({ children, icon, title, action }) {
  return (
    <div className="empty-state">
      <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 dark:bg-brand-950/50 dark:text-brand-300">
        {icon || (
          <svg
            className="h-7 w-7"
            viewBox="0 0 64 64"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <rect x="8" y="8" width="48" height="48" rx="10" />
            <path d="M8 40h14l4 6h12l4-6h14" />
            <path d="M24 24h16M24 32h10" />
          </svg>
        )}
      </div>
      {title && (
        <p className="mb-1.5 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">
          {title}
        </p>
      )}
      <p className="mx-auto max-w-sm text-sm leading-relaxed text-ink-700/70 dark:text-slate-400">{children}</p>
      {action && <div className="mt-6 flex justify-center">{action}</div>}
    </div>
  );
}
function PageHeader({ title, subtitle, action, eyebrow }) {
  return (
    <div className="page-header">
      <div className="relative min-w-0">
        {eyebrow && <p className="eyebrow mb-2.5">{eyebrow}</p>}
        <h1 className="font-display text-page-title text-ink-900 dark:text-slate-50">
          {title}
        </h1>
        {subtitle && (
          <p className="mt-2.5 max-w-2xl text-hero-sub text-ink-700/70 dark:text-slate-400">
            {subtitle}
          </p>
        )}
      </div>
      {action && <div className="relative flex shrink-0 flex-wrap items-center gap-2">{action}</div>}
    </div>
  );
}

function StatTile({ label, value }) {
  return (
    <div className="stat-tile">
      <p className="stat-tile-label">{label}</p>
      <p className="stat-tile-value">{value}</p>
    </div>
  );
}
const ROLE_STYLES = {
  admin: 'bg-brand-100 text-brand-800 dark:bg-brand-900/50 dark:text-brand-200',
  super_admin: 'bg-ink-900 text-white dark:bg-slate-100 dark:text-ink-900',
  editor: 'bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300',
  moderator: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-200',
  citizen: 'bg-ink-100 text-ink-700 dark:bg-slate-700 dark:text-slate-200',
};
const ORG_ROLE_STYLES = {
  owner: 'bg-brand-100 text-brand-800 dark:bg-brand-900/50 dark:text-brand-200',
  admin: 'bg-teal-100 text-teal-800 dark:bg-teal-900/40 dark:text-teal-200',
  content_manager: 'bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300',
  moderator: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-200',
  member: 'bg-ink-100 text-ink-600 dark:bg-slate-700 dark:text-slate-300',
};
function RoleBadge({
  role
}) {
  const {
    t
  } = useTranslation();
  const label = t(`admin.roles.${role}`, { defaultValue: role });
  return <span className={`badge ${ROLE_STYLES[role] ?? ROLE_STYLES.citizen}`} title={t("roles.platformRoleHint")}>{label}</span>;
}
function OrgRoleBadge({
  role
}) {
  const {
    t
  } = useTranslation();
  const label = t(`roles.org.${role}`, { defaultValue: role });
  return <span className={`badge ${ORG_ROLE_STYLES[role] ?? ORG_ROLE_STYLES.member}`} title={t("roles.orgRoleHint")}>{label}</span>;
}
function CardSkeleton() {
  return (
    <div className="content-tile flex flex-col gap-3">
      <div className="skeleton h-4 w-1/4" />
      <div className="skeleton h-5 w-3/4" />
      <div className="skeleton h-4 w-full" />
      <div className="skeleton h-4 w-5/6" />
      <div className="mt-2 flex justify-between">
        <div className="skeleton h-3 w-16" />
        <div className="skeleton h-3 w-20" />
      </div>
    </div>
  );
}

function StatCardSkeleton() {
  return (
    <div className="stat-tile flex flex-col gap-2">
      <div className="skeleton h-3 w-1/2" />
      <div className="skeleton h-8 w-1/3" />
    </div>
  );
}

function TableRowSkeleton({ cols = 5, rows = 1 }) {
  return (
    <>
      {Array.from({ length: rows }).map((_, r) => (
        <tr key={r}>
          {Array.from({ length: cols }).map((_, i) => (
            <td key={i} className="px-4 py-3">
              <div className="skeleton h-4 w-full" />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
}

function PasswordInput({ id, value, onChange, autoComplete, className = '', required, minLength, placeholder }) {
  const [show, setShow] = useState(false);
  return (
    <div className="relative">
      <input
        id={id}
        type={show ? 'text' : 'password'}
        value={value}
        onChange={onChange}
        autoComplete={autoComplete}
        required={required}
        minLength={minLength}
        placeholder={placeholder}
        className={`input pr-10 ${className}`}
      />
      <button
        type="button"
        aria-label={show ? 'Hide password' : 'Show password'}
        onClick={() => setShow((s) => !s)}
        className="absolute inset-y-0 right-0 flex min-w-11 items-center justify-center px-3 text-ink-700/45 hover:text-ink-700/80 dark:text-slate-500 dark:hover:text-slate-300"
        tabIndex={-1}
      >
        {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
      </button>
    </div>
  );
}

function passwordStrength(pw) {
  if (!pw) return 0;
  let score = 0;
  if (pw.length >= 8) score++;
  if (pw.length >= 12) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  return score;
}

const STRENGTH_LABELS = ['', 'Weak', 'Fair', 'Good', 'Strong', 'Very strong'];
const STRENGTH_COLORS = ['', 'bg-red-400', 'bg-amber-400', 'bg-yellow-400', 'bg-emerald-400', 'bg-emerald-500'];

function PasswordStrengthBar({ password }) {
  const strength = passwordStrength(password);
  if (!password) return null;
  return (
    <div className="mt-2">
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((i) => (
          <div
            key={i}
            className={`h-1 flex-1 rounded-full transition-colors ${i <= strength ? STRENGTH_COLORS[strength] : 'bg-ink-200 dark:bg-slate-600'}`}
          />
        ))}
      </div>
      <p className={`mt-1 text-xs font-medium ${strength >= 4 ? 'text-emerald-600 dark:text-emerald-400' : strength >= 2 ? 'text-amber-600 dark:text-amber-400' : 'text-red-600 dark:text-red-400'}`}>
        {STRENGTH_LABELS[strength]}
      </p>
    </div>
  );
}

function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel,
  cancelLabel,
  onConfirm,
  onCancel,
  busy = false,
  kind = 'danger',
}) {
  const { t } = useTranslation();
  const dialogRef = useRef(null);
  const cancelRef = useRef(null);
  const previousFocus = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    previousFocus.current = document.activeElement;
    const focusTimer = window.setTimeout(() => cancelRef.current?.focus(), 0);

    const onKeyDown = (e) => {
      if (e.key === 'Escape' && !busy) {
        e.preventDefault();
        onCancel();
        return;
      }
      if (e.key !== 'Tab' || !dialogRef.current) return;
      const focusable = dialogRef.current.querySelectorAll(
        'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
      );
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };

    document.addEventListener('keydown', onKeyDown);
    return () => {
      window.clearTimeout(focusTimer);
      document.removeEventListener('keydown', onKeyDown);
      if (previousFocus.current && typeof previousFocus.current.focus === 'function') {
        previousFocus.current.focus();
      }
    };
  }, [open, busy, onCancel]);

  if (!open) return null;

  const confirmClass = kind === 'danger' ? 'btn-danger' : 'btn-primary';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <button
        type="button"
        className="absolute inset-0 bg-black/50"
        aria-label={cancelLabel ?? t('common.cancel')}
        onClick={busy ? undefined : onCancel}
        tabIndex={-1}
      />
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
        aria-describedby={message ? 'confirm-dialog-desc' : undefined}
        className="relative w-full max-w-md rounded-xl border border-ink-100 bg-white p-6 shadow-xl dark:border-slate-700 dark:bg-slate-800"
      >
        <h2 id="confirm-dialog-title" className="font-display text-lg font-semibold text-ink-900 dark:text-slate-100">
          {title}
        </h2>
        {message && (
          <p id="confirm-dialog-desc" className="mt-2 text-sm text-ink-700/70 dark:text-slate-300">
            {message}
          </p>
        )}
        <div className="mt-6 flex flex-wrap justify-end gap-2">
          <button
            ref={cancelRef}
            type="button"
            className="btn-secondary"
            disabled={busy}
            onClick={onCancel}
          >
            {cancelLabel ?? t('common.cancel')}
          </button>
          <button type="button" className={confirmClass} disabled={busy} onClick={onConfirm}>
            {busy ? t('common.loading') : (confirmLabel ?? t('common.confirm'))}
          </button>
        </div>
      </div>
    </div>
  );
}

export { Alert, CardSkeleton, ConfirmDialog, EmptyState, OrgRoleBadge, PageHeader, PasswordInput, PasswordStrengthBar, RoleBadge, Spinner, StatCardSkeleton, StatTile, TableRowSkeleton };