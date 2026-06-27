import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Eye, EyeOff } from "./Icons";
function Spinner({
  label
}) {
  const {
    t
  } = useTranslation();
  return <div className="flex items-center justify-center gap-3 py-12 text-gray-500 dark:text-slate-400"><span className="h-5 w-5 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" /><span>{label ?? t("common.loading")}</span></div>;
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
  return <div className={`rounded-lg border px-4 py-3 text-sm ${styles}`}>{children}</div>;
}
function EmptyState({ children, icon }) {
  return (
    <div className="rounded-xl border border-dashed border-gray-300 bg-white py-12 text-center text-gray-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
      {icon || (
        <svg className="mx-auto mb-4 h-12 w-12 text-gray-300 dark:text-slate-600" viewBox="0 0 64 64" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="8" y="8" width="48" height="48" rx="6" />
          <path d="M8 40h14l4 6h12l4-6h14" />
          <path d="M24 24h16M24 32h10" />
        </svg>
      )}
      <p className="text-sm">{children}</p>
    </div>
  );
}
function PageHeader({
  title,
  subtitle,
  action
}) {
  return <div className="mb-6 flex items-center justify-between gap-4"><div><h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100">{title}</h1>{subtitle && <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">{subtitle}</p>}</div>{action}</div>;
}
const ROLE_STYLES = {
  admin: "bg-purple-100 text-purple-700",
  editor: "bg-brand-100 text-brand-700",
  moderator: "bg-amber-100 text-amber-700",
  citizen: "bg-gray-100 text-gray-700"
};
const ORG_ROLE_STYLES = {
  owner: "bg-brand-100 text-brand-800",
  admin: "bg-teal-100 text-teal-700",
  member: "bg-gray-100 text-gray-600"
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
    <div className="card flex flex-col gap-3">
      <div className="skeleton h-40 w-full" />
      <div className="skeleton h-4 w-1/3" />
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
    <div className="card flex flex-col gap-2">
      <div className="skeleton h-4 w-1/2" />
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
        className="absolute inset-y-0 right-0 flex items-center px-3 text-gray-400 hover:text-gray-600 dark:text-slate-500 dark:hover:text-slate-300"
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
            className={`h-1 flex-1 rounded-full transition-colors ${i <= strength ? STRENGTH_COLORS[strength] : 'bg-gray-200 dark:bg-slate-600'}`}
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

  useEffect(() => {
    if (!open) return undefined;
    const onKeyDown = (e) => {
      if (e.key === 'Escape' && !busy) onCancel();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
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
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
        className="relative w-full max-w-md rounded-xl border border-gray-200 bg-white p-6 shadow-xl dark:border-slate-700 dark:bg-slate-800"
      >
        <h2 id="confirm-dialog-title" className="text-lg font-semibold text-gray-900 dark:text-slate-100">
          {title}
        </h2>
        {message && (
          <p className="mt-2 text-sm text-gray-600 dark:text-slate-300">{message}</p>
        )}
        <div className="mt-6 flex flex-wrap justify-end gap-2">
          <button type="button" className="btn-secondary" disabled={busy} onClick={onCancel}>
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

export { Alert, CardSkeleton, ConfirmDialog, EmptyState, OrgRoleBadge, PageHeader, PasswordInput, PasswordStrengthBar, passwordStrength, RoleBadge, Spinner, StatCardSkeleton, TableRowSkeleton };