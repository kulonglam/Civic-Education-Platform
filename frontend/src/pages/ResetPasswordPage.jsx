import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useSearchParams } from 'react-router-dom';
import { authService } from '../lib/services';
import { extractError } from '../lib/api';
import { Alert, PasswordInput } from '../components/ui';
import { ShieldCheck } from '../components/Icons';

export function ResetPasswordPage() {
  const { t } = useTranslation();
  const [params] = useSearchParams();
  const uid = params.get('uid') ?? '';
  const token = params.get('token') ?? '';
  const otpMode = params.get('mode') === 'otp' || (!uid && !token);

  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (otpMode) {
        await authService.confirmResetOtp(phone, code, password);
      } else {
        await authService.confirmReset(uid, token, password);
      }
      setDone(true);
    } catch (err) {
      setError(extractError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-md">
      <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
        {/* Branded header */}
        <div className="bg-gradient-to-br from-brand-600 to-brand-700 px-8 py-8 text-white">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/20">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold">{t('auth.resetTitle')}</h1>
              <p className="text-sm text-brand-100">{t('auth.resetSubtitle')}</p>
            </div>
          </div>
        </div>

        <div className="p-6">
          {done ? (
            <>
              <Alert kind="success">{t('auth.verifySuccess')}</Alert>
              <Link to="/login" className="btn-primary mt-4 block w-full text-center">
                {t('nav.login')}
              </Link>
            </>
          ) : (
            <>
              {error && (
                <div className="mb-4">
                  <Alert>{error}</Alert>
                </div>
              )}
              <form onSubmit={submit} className="space-y-4">
                {otpMode && (
                  <>
                    <div>
                      <label className="label">{t('profile.phone')}</label>
                      <input
                        type="tel"
                        className="input"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <label className="label">{t('sms.otpCode')}</label>
                      <input
                        className="input"
                        value={code}
                        onChange={(e) => setCode(e.target.value)}
                        required
                        maxLength={6}
                      />
                    </div>
                  </>
                )}
                <div>
                  <label className="label">{t('auth.newPassword')}</label>
                  <PasswordInput
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="new-password"
                    minLength={8}
                    required
                  />
                </div>
                <button type="submit" className="btn-primary w-full" disabled={loading}>
                  {loading ? t('common.loading') : t('common.submit')}
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
