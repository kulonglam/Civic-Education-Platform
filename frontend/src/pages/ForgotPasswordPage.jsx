import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { authService } from '../lib/services';
import { extractError } from '../lib/api';
import { Alert } from '../components/ui';
import { ShieldCheck } from '../components/Icons';

export function ForgotPasswordPage() {
  const { t } = useTranslation();
  const [mode, setMode] = useState('email');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submitEmail = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authService.requestReset(email);
      setSent(true);
    } catch (err) {
      setError(extractError(err));
    } finally {
      setLoading(false);
    }
  };

  const submitPhone = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authService.requestResetOtp(phone);
      setSent(true);
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
              <h1 className="text-xl font-bold">{t('auth.resetRequestTitle')}</h1>
              <p className="text-sm text-brand-100">{t('auth.resetRequestSubtitle')}</p>
            </div>
          </div>
        </div>

        <div className="p-6">
          <div className="mb-4 flex gap-2">
            <button
              type="button"
              className={mode === 'email' ? 'btn-primary flex-1' : 'btn-secondary flex-1'}
              onClick={() => {
                setMode('email');
                setSent(false);
                setError('');
              }}
            >
              {t('auth.email')}
            </button>
            <button
              type="button"
              className={mode === 'phone' ? 'btn-primary flex-1' : 'btn-secondary flex-1'}
              onClick={() => {
                setMode('phone');
                setSent(false);
                setError('');
              }}
            >
              {t('profile.phone')}
            </button>
          </div>

          {sent ? (
            <Alert kind="success">
              {mode === 'email' ? t('auth.resetSent') : t('sms.otpSent')}
            </Alert>
          ) : (
            <>
              {error && (
                <div className="mb-4">
                  <Alert>{error}</Alert>
                </div>
              )}
              {mode === 'email' ? (
                <form onSubmit={submitEmail} className="space-y-4">
                  <div>
                    <label className="label">{t('auth.email')}</label>
                    <input
                      type="email"
                      className="input"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                  <button type="submit" className="btn-primary w-full" disabled={loading}>
                    {loading ? t('common.loading') : t('auth.sendResetLink')}
                  </button>
                </form>
              ) : (
                <form onSubmit={submitPhone} className="space-y-4">
                  <div>
                    <label className="label">{t('profile.phone')}</label>
                    <input
                      type="tel"
                      className="input"
                      placeholder="+211922123456"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      required
                    />
                  </div>
                  <button type="submit" className="btn-primary w-full" disabled={loading}>
                    {loading ? t('common.loading') : t('sms.sendOtp')}
                  </button>
                  <p className="text-sm text-gray-500 dark:text-slate-400">{t('sms.otpResetHint')}</p>
                </form>
              )}
            </>
          )}

          {sent && mode === 'phone' && (
            <Link to="/reset-password?mode=otp" className="btn-secondary mt-4 block w-full text-center">
              {t('sms.enterOtpCode')}
            </Link>
          )}

          <p className="mt-4 text-center text-sm">
            <Link to="/login" className="text-brand-600 hover:underline dark:text-brand-400">
              {t('common.back')}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
