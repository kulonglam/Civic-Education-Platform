import { useEffect, useState, type ChangeEvent, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useSearchParams } from 'react-router-dom';
import { authService } from '../lib/services';
import type { RegisterPayload } from '../types/api';
import { extractError } from '../lib/api';
import { Alert, PasswordInput, PasswordStrengthBar } from '../components/ui';
import { AuthShell } from '../components/AuthShell';

export function RegisterPage() {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const inviteToken = searchParams.get('invite') ?? '';
  const prefilledEmail = searchParams.get('email') ?? '';
  const typeParam = searchParams.get('type');
  const initialAccountType =
    typeParam === 'organization' ? 'organization' : 'citizen';

  const [accountType, setAccountType] = useState(initialAccountType);
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: prefilledEmail,
    password: '',
    password_confirm: '',
    organization_name: '',
    invite_token: inviteToken,
    account_type: initialAccountType,
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setForm((f) => ({
      ...f,
      email: prefilledEmail || f.email,
      invite_token: inviteToken || f.invite_token,
    }));
  }, [prefilledEmail, inviteToken]);

  useEffect(() => {
    if (!inviteToken) {
      setAccountType(initialAccountType);
      setForm((f) => ({ ...f, account_type: initialAccountType }));
    }
  }, [initialAccountType, inviteToken]);

  const update = (key: string) => (e: ChangeEvent<HTMLInputElement>) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const selectAccountType = (type: string) => {
    setAccountType(type);
    setForm((f) => ({ ...f, account_type: type }));
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload: RegisterPayload = { ...form, account_type: accountType };
      if (payload.invite_token) {
        delete payload.organization_name;
        delete payload.account_type;
      } else if (accountType === 'citizen') {
        delete payload.organization_name;
      }
      const { data } = await authService.register(payload as RegisterPayload);
      setSuccessMessage(data?.email_sent === false ? (data.message || '') : '');
      setSuccess(true);
    } catch (err) {
      setError(extractError(err));
    } finally {
      setLoading(false);
    }
  };

  const joiningViaInvite = Boolean(form.invite_token);
  const isOrganization = accountType === 'organization';

  const panelTitle = joiningViaInvite
    ? t('saas.registerViaInvite')
    : isOrganization
      ? t('auth.registerOrgTitle')
      : t('auth.registerCitizenTitle');

  if (success) {
    const copy = successMessage || t('auth.registerSuccess');
    return (
      <AuthShell title={t('auth.registerSuccessTitle')} subtitle={copy} showBrand={false}>
        <Alert kind={successMessage ? 'warning' : 'success'}>{copy}</Alert>
        <Link to="/login" className="btn-primary mt-6 w-full">
          {t('nav.login')}
        </Link>
      </AuthShell>
    );
  }

  return (
    <AuthShell
      title={t('auth.registerPanelTitle')}
      subtitle={
        joiningViaInvite
          ? t('saas.registerViaInvite')
          : isOrganization
            ? t('auth.accountTypeOrganizationHint')
            : t('auth.accountTypeCitizenHint')
      }
      showBrand={false}
    >
      <p className="eyebrow">{t('auth.getStarted')}</p>
      <h2 className="mt-2 font-display text-2xl font-semibold text-ink-900 dark:text-slate-50">
        {panelTitle}
      </h2>

      {error && (
        <div className="mt-5">
          <Alert id="register-error">{error}</Alert>
        </div>
      )}

      {!joiningViaInvite && (
        <div className="mt-6 grid grid-cols-2 gap-1 rounded-xl border border-ink-100 bg-ink-50/80 p-1 dark:border-slate-700 dark:bg-slate-900/50">
          <button
            type="button"
            className={`min-h-11 rounded-lg px-3 py-2.5 text-sm font-semibold transition-colors ${
              accountType === 'citizen'
                ? 'bg-white text-brand-800 shadow-soft dark:bg-slate-800 dark:text-brand-300'
                : 'text-ink-700/70 hover:text-ink-900 dark:text-slate-400'
            }`}
            aria-pressed={accountType === 'citizen'}
            onClick={() => selectAccountType('citizen')}
          >
            {t('auth.accountTypeCitizen')}
          </button>
          <button
            type="button"
            className={`min-h-11 rounded-lg px-3 py-2.5 text-sm font-semibold transition-colors ${
              accountType === 'organization'
                ? 'bg-white text-brand-800 shadow-soft dark:bg-slate-800 dark:text-brand-300'
                : 'text-ink-700/70 hover:text-ink-900 dark:text-slate-400'
            }`}
            aria-pressed={accountType === 'organization'}
            onClick={() => selectAccountType('organization')}
          >
            {t('auth.accountTypeOrganization')}
          </button>
        </div>
      )}

      <form onSubmit={submit} className="mt-6 space-y-4" aria-describedby={error ? 'register-error' : undefined}>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label" htmlFor="first_name">
              {t('auth.firstName')}
            </label>
            <input
              id="first_name"
              className="input"
              value={form.first_name}
              onChange={update('first_name')}
              required
            />
          </div>
          <div>
            <label className="label" htmlFor="last_name">
              {t('auth.lastName')}
            </label>
            <input
              id="last_name"
              className="input"
              value={form.last_name}
              onChange={update('last_name')}
              required
            />
          </div>
        </div>
        {!joiningViaInvite && isOrganization && (
          <div>
            <label className="label" htmlFor="organization_name">
              {t('saas.orgName')}
            </label>
            <input
              id="organization_name"
              className="input"
              value={form.organization_name}
              onChange={update('organization_name')}
              placeholder={t('saas.orgNamePlaceholder')}
            />
          </div>
        )}
        <div>
          <label className="label" htmlFor="email">
            {t('auth.email')}
          </label>
          <input
            id="email"
            type="email"
            className="input"
            value={form.email}
            onChange={update('email')}
            readOnly={joiningViaInvite && Boolean(prefilledEmail)}
            autoComplete="email"
            aria-invalid={Boolean(error)}
            aria-describedby={error ? 'register-error' : undefined}
            required
          />
        </div>
        <div>
          <label className="label" htmlFor="password">
            {t('auth.password')}
          </label>
          <PasswordInput
            id="password"
            value={form.password}
            onChange={update('password')}
            autoComplete="new-password"
            minLength={8}
            aria-invalid={Boolean(error)}
            aria-describedby={error ? 'register-error' : undefined}
            required
          />
          <PasswordStrengthBar password={form.password} />
        </div>
        <div>
          <label className="label" htmlFor="password_confirm">
            {t('auth.confirmPassword')}
          </label>
          <PasswordInput
            id="password_confirm"
            value={form.password_confirm}
            onChange={update('password_confirm')}
            autoComplete="new-password"
            aria-invalid={Boolean(error)}
            aria-describedby={error ? 'register-error' : undefined}
            required
          />
        </div>
        <button type="submit" className="btn-primary w-full" disabled={loading}>
          {loading ? t('common.loading') : t('nav.register')}
        </button>
      </form>
      <p className="mt-5 text-center text-sm text-ink-700/65 dark:text-slate-400">
        {t('auth.haveAccount')}{' '}
        <Link to="/login" className="font-semibold text-brand-700 hover:underline dark:text-brand-400">
          {t('nav.login')}
        </Link>
      </p>
    </AuthShell>
  );
}
