import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useSearchParams } from 'react-router-dom';
import { authService } from '../lib/services';
import { extractError } from '../lib/api';
import { Alert, PasswordInput, PasswordStrengthBar } from '../components/ui';
import { PlatformLogo } from '../components/PlatformLogo';

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

  const update = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const selectAccountType = (type) => {
    setAccountType(type);
    setForm((f) => ({ ...f, account_type: type }));
  };

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload = { ...form, account_type: accountType };
      if (payload.invite_token) {
        delete payload.organization_name;
        delete payload.account_type;
      } else if (accountType === 'citizen') {
        delete payload.organization_name;
      }
      await authService.register(payload);
      setSuccess(true);
    } catch (err) {
      setError(extractError(err));
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="mx-auto max-w-md">
        <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-md dark:border-slate-700 dark:bg-slate-800">
          <div className="bg-gradient-to-br from-brand-700 to-brand-900 px-8 py-6 text-white">
            <div className="flex items-center gap-3">
              <PlatformLogo className="h-10 w-10 rounded-lg bg-white/10 p-1" />
              <div>
                <p className="font-bold">{t('app.name')}</p>
                <p className="text-xs text-brand-200">{t('app.tagline')}</p>
              </div>
            </div>
          </div>
          <div className="px-8 py-6">
            <Alert kind="success">{t('auth.registerSuccess')}</Alert>
            <Link to="/login" className="btn-primary mt-4 w-full">
              {t('nav.login')}
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const joiningViaInvite = Boolean(form.invite_token);
  const isOrganization = accountType === 'organization';

  return (
    <div className="mx-auto max-w-md">
      <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-md dark:border-slate-700 dark:bg-slate-800">
        {/* Brand header */}
        <div className="bg-gradient-to-br from-brand-700 to-brand-900 px-8 py-6 text-white">
          <div className="flex items-center gap-3">
            <PlatformLogo className="h-12 w-12 rounded-lg bg-white/10 p-1" />
            <div>
              <p className="font-bold">{t('app.name')}</p>
              <p className="text-xs text-brand-200">{t('app.tagline')}</p>
            </div>
          </div>
        </div>
        <div className="px-8 py-6">
        <h1 className="mb-2 text-2xl font-bold">
          {joiningViaInvite
            ? t('saas.registerViaInvite')
            : isOrganization
              ? t('auth.registerOrgTitle')
              : t('auth.registerCitizenTitle')}
        </h1>
        {!joiningViaInvite && (
          <p className="mb-6 text-sm text-gray-500">
            {isOrganization ? t('auth.accountTypeOrganizationHint') : t('auth.accountTypeCitizenHint')}
          </p>
        )}
        {error && (
          <div className="mb-4">
            <Alert>{error}</Alert>
          </div>
        )}

        {!joiningViaInvite && (
          <div className="mb-6 grid grid-cols-2 gap-2 rounded-lg bg-gray-100 p-1">
            <button
              type="button"
              className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                accountType === 'citizen'
                  ? 'bg-white text-brand-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              onClick={() => selectAccountType('citizen')}
            >
              {t('auth.accountTypeCitizen')}
            </button>
            <button
              type="button"
              className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                accountType === 'organization'
                  ? 'bg-white text-brand-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              onClick={() => selectAccountType('organization')}
            >
              {t('auth.accountTypeOrganization')}
            </button>
          </div>
        )}

        <form onSubmit={submit} className="space-y-4">
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
              required
            />
          </div>
          <button type="submit" className="btn-primary w-full" disabled={loading}>
            {loading ? t('common.loading') : t('nav.register')}
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-500 dark:text-slate-400">
          {t('auth.haveAccount')}{' '}
          <Link to="/login" className="text-brand-600 hover:underline dark:text-brand-400">
            {t('nav.login')}
          </Link>
        </p>
        </div>
      </div>
    </div>
  );
}
