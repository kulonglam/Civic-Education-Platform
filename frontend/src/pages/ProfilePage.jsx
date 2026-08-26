import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import { authService, notificationService, userService } from '../lib/services';
import { extractError } from '../lib/api';
import { GamificationSummary } from '../components/GamificationSummary';
import { ConfirmDialog, OrgRoleBadge, PageHeader, PasswordInput, PasswordStrengthBar, RoleBadge } from '../components/ui';
import { CloudArrowDown } from '../components/Icons';
import { AGE_BAND_OPTIONS, REGION_OPTIONS } from '../lib/demographics';
import { formatDate } from '../lib/format';
import { downloadContentBundle, getContentBundleMeta } from '../lib/offline/contentBundle';

const VAPID_PUBLIC_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY || '';

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const raw = window.atob(base64);
  return Uint8Array.from([...raw].map((char) => char.charCodeAt(0)));
}

export function ProfilePage() {
  const { t, i18n } = useTranslation();
  const { user, refreshUser, logout } = useAuth();
  const { membership } = useOrganization();
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    bio: '',
    avatar_url: '',
    preferred_language: 'en',
    region: '',
    age_band: '',
    show_on_leaderboard: true,
    whatsapp_alerts: false,
  });
  const [loading, setLoading] = useState(false);
  const [avatarUploading, setAvatarUploading] = useState(false);
  const [verifyCode, setVerifyCode] = useState('');
  const [verifyBusy, setVerifyBusy] = useState('');
  const [verifyMessage, setVerifyMessage] = useState('');
  const [verifyError, setVerifyError] = useState('');
  const [pushSupported, setPushSupported] = useState(false);
  const [pushEnabled, setPushEnabled] = useState(false);
  const [pushBusy, setPushBusy] = useState(false);
  const [pwForm, setPwForm] = useState({ current_password: '', new_password: '', confirm: '' });
  const [pwLoading, setPwLoading] = useState(false);
  const [mfaSetup, setMfaSetup] = useState(null);
  const [mfaCode, setMfaCode] = useState('');
  const [mfaBusy, setMfaBusy] = useState('');
  const [dataBusy, setDataBusy] = useState('');
  const [deactivateOpen, setDeactivateOpen] = useState(false);
  const [bundleBusy, setBundleBusy] = useState(false);
  const [bundleMeta, setBundleMeta] = useState(null);
  const [bundleError, setBundleError] = useState('');

  useEffect(() => {
    if (!VAPID_PUBLIC_KEY || !('Notification' in window) || !('serviceWorker' in navigator)) {
      setPushSupported(false);
      return;
    }
    setPushSupported(true);
    navigator.serviceWorker.ready
      .then((registration) => registration.pushManager.getSubscription())
      .then((subscription) => setPushEnabled(!!subscription))
      .catch(() => setPushEnabled(false));
  }, [user?.id]);

  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name,
        last_name: user.last_name,
        phone: user.phone ?? '',
        bio: user.profile?.bio ?? '',
        avatar_url: user.profile?.avatar_url ?? '',
        preferred_language: user.profile?.preferred_language ?? 'en',
        region: user.profile?.region ?? '',
        age_band: user.profile?.age_band ?? '',
        show_on_leaderboard: user.profile?.show_on_leaderboard !== false,
        whatsapp_alerts: Boolean(user.whatsapp_alerts),
      });
    }
  }, [user]);

  useEffect(() => {
    getContentBundleMeta().then(setBundleMeta).catch(() => setBundleMeta(null));
  }, []);

  const downloadStudyPack = async () => {
    setBundleBusy(true);
    setBundleError('');
    try {
      const summary = await downloadContentBundle();
      setBundleMeta(summary);
      toast.success(
        t('offline.bundleDownloaded', {
          articles: summary.articles,
          quizzes: summary.quizzes,
        }),
      );
    } catch (err) {
      setBundleError(extractError(err));
    } finally {
      setBundleBusy(false);
    }
  };

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await userService.updateProfile(form);
      await refreshUser();
      toast.success(t('profile.saved'));
      if (form.preferred_language !== i18n.language) {
        i18n.changeLanguage(form.preferred_language);
      }
    } catch (err) {
      toast.error(extractError(err));
    } finally {
      setLoading(false);
    }
  };

  const sendPhoneCode = async () => {
    setVerifyBusy('send');
    setVerifyError('');
    setVerifyMessage('');
    try {
      const { data } = await authService.sendPhoneVerify();
      setVerifyMessage(data.message || t('phoneVerify.codeSent'));
    } catch (err) {
      setVerifyError(extractError(err));
    } finally {
      setVerifyBusy('');
    }
  };

  const confirmPhoneCode = async (e) => {
    e.preventDefault();
    setVerifyBusy('confirm');
    setVerifyError('');
    setVerifyMessage('');
    try {
      const { data } = await authService.confirmPhoneVerify(verifyCode);
      setVerifyMessage(data.message || t('phoneVerify.verified'));
      setVerifyCode('');
      await refreshUser();
    } catch (err) {
      setVerifyError(extractError(err));
    } finally {
      setVerifyBusy('');
    }
  };

  const enablePush = async () => {
    setPushBusy(true);
    try {
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        toast.error(t('push.permissionDenied'));
        return;
      }
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
      });
      const json = subscription.toJSON();
      await notificationService.subscribePush({
        endpoint: json.endpoint,
        keys: json.keys,
      });
      setPushEnabled(true);
      toast.success(t('push.enabled'));
    } catch (err) {
      toast.error(extractError(err));
    } finally {
      setPushBusy(false);
    }
  };

  const disablePush = async () => {
    setPushBusy(true);
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      if (subscription) {
        const json = subscription.toJSON();
        await notificationService.unsubscribePush({
          endpoint: json.endpoint,
          keys: json.keys,
        });
        await subscription.unsubscribe();
      }
      setPushEnabled(false);
      toast.success(t('push.disabled'));
    } catch (err) {
      toast.error(extractError(err));
    } finally {
      setPushBusy(false);
    }
  };

  const changePassword = async (e) => {
    e.preventDefault();
    if (pwForm.new_password !== pwForm.confirm) {
      toast.error(t('auth.passwordMismatch'));
      return;
    }
    setPwLoading(true);
    try {
      await authService.changePassword(pwForm.current_password, pwForm.new_password);
      toast.success(t('profile.passwordChanged'));
      setPwForm({ current_password: '', new_password: '', confirm: '' });
    } catch (err) {
      toast.error(extractError(err));
    } finally {
      setPwLoading(false);
    }
  };

  const startMfaSetup = async () => {
    setMfaBusy('setup');
    try {
      const { data } = await authService.mfaSetup();
      setMfaSetup(data);
      setMfaCode('');
    } catch (err) {
      toast.error(extractError(err));
    } finally {
      setMfaBusy('');
    }
  };

  const confirmMfaSetup = async (e) => {
    e.preventDefault();
    setMfaBusy('confirm');
    try {
      await authService.mfaConfirmSetup(mfaCode.trim());
      setMfaSetup(null);
      setMfaCode('');
      await refreshUser();
      toast.success(t('profile.mfaSetupSuccess'));
    } catch (err) {
      toast.error(extractError(err));
    } finally {
      setMfaBusy('');
    }
  };

  const downloadMyData = async () => {
    setDataBusy('export');
    try {
      const { data } = await userService.exportMyData();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'my-civic-data.json';
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      toast.error(extractError(err));
    } finally {
      setDataBusy('');
    }
  };

  const confirmDeactivate = async () => {
    setDataBusy('deactivate');
    try {
      await userService.deactivate();
      setDeactivateOpen(false);
      toast.success(t('profile.deactivateSuccess'));
      await logout();
    } catch (err) {
      toast.error(extractError(err));
    } finally {
      setDataBusy('');
    }
  };

  const uploadAvatar = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAvatarUploading(true);
    try {
      const { data } = await userService.uploadAvatar(file);
      setForm((f) => ({ ...f, avatar_url: data.avatar_url ?? f.avatar_url }));
      await refreshUser();
      toast.success(t('profile.saved'));
    } catch (err) {
      toast.error(extractError(err));
    } finally {
      setAvatarUploading(false);
      e.target.value = '';
    }
  };

  if (!user) return null;

  return (
    <div className="mx-auto max-w-2xl">
      <PageHeader title={t('profile.title')} />
      <div className="card mb-6 flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-100 text-2xl font-bold text-brand-700">
          {form.avatar_url ? (
            <img src={form.avatar_url} alt="" className="h-16 w-16 rounded-full object-cover" />
          ) : (
            user.first_name.charAt(0)
          )}
        </div>
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-lg font-semibold">
              {user.first_name} {user.last_name}
            </h2>
            <RoleBadge role={user.role.name} />
            {membership && <OrgRoleBadge role={membership.role} />}
          </div>
          <p className="text-sm text-ink-700/60">{user.email}</p>
          <p className="text-xs text-ink-700/70">
            {t('profile.memberSince')} {formatDate(user.created_at)}
          </p>
        </div>
      </div>
      <div className="card mb-6">
        <GamificationSummary />
      </div>
      <form onSubmit={submit} className="card space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">{t('auth.firstName')}</label>
            <input
              className="input"
              value={form.first_name}
              onChange={(e) => setForm((f) => ({ ...f, first_name: e.target.value }))}
            />
          </div>
          <div>
            <label className="label">{t('auth.lastName')}</label>
            <input
              className="input"
              value={form.last_name}
              onChange={(e) => setForm((f) => ({ ...f, last_name: e.target.value }))}
            />
          </div>
        </div>
        <div>
          <label className="label">{t('profile.phone')}</label>
          <input
            type="tel"
            className="input"
            placeholder="+256772123456"
            value={form.phone}
            onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
          />
          <p className="mt-1 text-xs text-ink-700/60">{t('profile.phoneHint')}</p>
          {user.phone && user.phone_verified && (
            <p className="mt-1 text-xs font-medium text-green-700">{t('phoneVerify.verifiedBadge')}</p>
          )}
          {form.phone && !user.phone_verified && (
            <div className="mt-3 rounded-lg border border-amber-100 bg-amber-50 p-3">
              <p className="text-sm text-amber-900">{t('phoneVerify.hint')}</p>
              {verifyMessage && <p className="mt-1 text-xs text-green-700">{verifyMessage}</p>}
              {verifyError && <p className="mt-1 text-xs text-red-700">{verifyError}</p>}
              <div className="mt-3 flex flex-wrap gap-2">
                <button
                  type="button"
                  className="btn-secondary text-sm"
                  onClick={sendPhoneCode}
                  disabled={!!verifyBusy}
                >
                  {verifyBusy === 'send' ? t('common.loading') : t('phoneVerify.sendCode')}
                </button>
              </div>
              <form onSubmit={confirmPhoneCode} className="mt-3 flex flex-wrap items-end gap-2">
                <div className="flex-1">
                  <label className="label">{t('phoneVerify.enterCode')}</label>
                  <input
                    className="input"
                    inputMode="numeric"
                    maxLength={6}
                    value={verifyCode}
                    onChange={(e) => setVerifyCode(e.target.value)}
                    placeholder="123456"
                  />
                </div>
                <button type="submit" className="btn-primary text-sm" disabled={!verifyCode.trim() || !!verifyBusy}>
                  {verifyBusy === 'confirm' ? t('common.loading') : t('phoneVerify.confirm')}
                </button>
              </form>
            </div>
          )}
        </div>
        <div>
          <label className="label">{t('profile.bio')}</label>
          <textarea
            className="input min-h-[80px]"
            value={form.bio}
            onChange={(e) => setForm((f) => ({ ...f, bio: e.target.value }))}
          />
        </div>
        <div>
          <label className="label">{t('profile.avatarUpload')}</label>
          <input
            type="file"
            accept="image/*"
            className="input"
            onChange={uploadAvatar}
            disabled={avatarUploading}
          />
          <p className="mt-1 text-xs text-ink-700/60">{t('profile.avatarUploadHint')}</p>
        </div>
        <div>
          <label className="label">{t('profile.avatarUrl')}</label>
          <input
            className="input"
            value={form.avatar_url}
            onChange={(e) => setForm((f) => ({ ...f, avatar_url: e.target.value }))}
          />
        </div>
        <div>
          <label className="label">{t('profile.language')}</label>
          <select
            className="input"
            value={form.preferred_language}
            onChange={(e) => setForm((f) => ({ ...f, preferred_language: e.target.value }))}
          >
            <option value="en">English</option>
            <option value="ar">العربية</option>
          </select>
        </div>
        <div>
          <label className="label">{t('profile.region')}</label>
          <select
            className="input"
            value={form.region}
            onChange={(e) => setForm((f) => ({ ...f, region: e.target.value }))}
          >
            {REGION_OPTIONS.map((option) => (
              <option key={option.value || 'unset'} value={option.value}>{t(option.labelKey)}</option>
            ))}
          </select>
          <p className="mt-1 text-xs text-ink-700/60">{t('profile.regionHint')}</p>
        </div>
        <div>
          <label className="label">{t('profile.ageBand')}</label>
          <select
            className="input"
            value={form.age_band}
            onChange={(e) => setForm((f) => ({ ...f, age_band: e.target.value }))}
          >
            {AGE_BAND_OPTIONS.map((option) => (
              <option key={option.value || 'unset'} value={option.value}>{t(option.labelKey)}</option>
            ))}
          </select>
          <p className="mt-1 text-xs text-ink-700/60">{t('profile.ageHint')}</p>
        </div>
        <label className="flex items-center gap-2 text-sm font-medium">
          <input
            type="checkbox"
            checked={form.show_on_leaderboard}
            onChange={(e) => setForm((f) => ({ ...f, show_on_leaderboard: e.target.checked }))}
          />
          {t('profile.showOnLeaderboard')}
        </label>
        <label className="flex items-center gap-2 text-sm font-medium">
          <input
            type="checkbox"
            checked={form.whatsapp_alerts}
            onChange={(e) => setForm((f) => ({ ...f, whatsapp_alerts: e.target.checked }))}
          />
          {t('profile.whatsappAlerts')}
        </label>
        <p className="text-xs text-ink-700/60">{t('profile.whatsappHint')}</p>
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? t('common.loading') : t('common.save')}
        </button>
      </form>

      {(user.mfa_required || user.mfa_enabled) && (
        <div className="card mt-6 space-y-4">
          <h2 className="text-sm font-semibold text-ink-900 dark:text-slate-100">{t('profile.mfaTitle')}</h2>
          {user.mfa_enabled ? (
            <p className="text-sm text-green-700 dark:text-green-400">{t('profile.mfaEnabled')}</p>
          ) : (
            <>
              <p className="text-sm text-amber-800 dark:text-amber-200">{t('profile.mfaRequiredHint')}</p>
              {!mfaSetup ? (
                <button type="button" className="btn-secondary text-sm" onClick={startMfaSetup} disabled={!!mfaBusy}>
                  {mfaBusy === 'setup' ? t('common.loading') : t('profile.mfaStartSetup')}
                </button>
              ) : (
                <form onSubmit={confirmMfaSetup} className="space-y-3">
                  <div>
                    <label className="label">{t('profile.mfaSecretLabel')}</label>
                    <code className="block break-all rounded bg-ink-100 px-2 py-1 text-xs dark:bg-slate-900">
                      {mfaSetup.secret}
                    </code>
                  </div>
                  <div>
                    <label className="label">{t('profile.mfaConfirmCode')}</label>
                    <input
                      className="input"
                      inputMode="numeric"
                      maxLength={6}
                      value={mfaCode}
                      onChange={(e) => setMfaCode(e.target.value)}
                      required
                    />
                  </div>
                  <button type="submit" className="btn-primary text-sm" disabled={!!mfaBusy || mfaCode.trim().length < 6}>
                    {mfaBusy === 'confirm' ? t('common.loading') : t('profile.mfaConfirm')}
                  </button>
                </form>
              )}
            </>
          )}
        </div>
      )}

      {/* Change password */}
      <form onSubmit={changePassword} className="card mt-6 space-y-4">
        <h2 className="text-sm font-semibold text-ink-900 dark:text-slate-100">{t('profile.changePassword')}</h2>
        <div>
          <label className="label">{t('profile.currentPassword')}</label>
          <PasswordInput
            value={pwForm.current_password}
            onChange={(e) => setPwForm((f) => ({ ...f, current_password: e.target.value }))}
            autoComplete="current-password"
            required
          />
        </div>
        <div>
          <label className="label">{t('auth.newPassword')}</label>
          <PasswordInput
            value={pwForm.new_password}
            onChange={(e) => setPwForm((f) => ({ ...f, new_password: e.target.value }))}
            autoComplete="new-password"
            minLength={8}
            required
          />
          <PasswordStrengthBar password={pwForm.new_password} />
        </div>
        <div>
          <label className="label">{t('auth.confirmNewPassword')}</label>
          <PasswordInput
            value={pwForm.confirm}
            onChange={(e) => setPwForm((f) => ({ ...f, confirm: e.target.value }))}
            autoComplete="new-password"
            minLength={8}
            required
          />
        </div>
        <button type="submit" className="btn-primary" disabled={pwLoading}>
          {pwLoading ? t('common.loading') : t('profile.changePassword')}
        </button>
      </form>

      <div className="card mt-6 space-y-3">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
            <CloudArrowDown className="h-5 w-5" />
          </div>
          <div className="min-w-0 flex-1">
            <h2 className="text-sm font-semibold text-ink-900 dark:text-slate-100">{t('offline.bundleTitle')}</h2>
            <p className="mt-1 text-sm text-ink-700/80 dark:text-slate-400">{t('offline.bundleHint')}</p>
            {bundleMeta && (
              <p className="mt-2 text-xs text-ink-700/60 dark:text-slate-500">
                {t('offline.bundleStatus', {
                  articles: bundleMeta.articles,
                  quizzes: bundleMeta.quizzes,
                })}
              </p>
            )}
            {bundleError && <p className="mt-2 text-xs text-red-600">{bundleError}</p>}
            <button
              type="button"
              className="btn-primary mt-3 text-sm"
              onClick={downloadStudyPack}
              disabled={bundleBusy}
            >
              {bundleBusy ? t('common.loading') : t('offline.bundleDownload')}
            </button>
          </div>
        </div>
      </div>

      {pushSupported && (
        <div className="card mt-6 space-y-3">
          <h2 className="text-sm font-semibold text-ink-900 dark:text-slate-100">{t('push.profileTitle')}</h2>
          <p className="text-sm text-ink-700/80">{t('push.profileHint')}</p>
          <div className="flex flex-wrap gap-2">
            {pushEnabled ? (
              <button type="button" className="btn-secondary text-sm" onClick={disablePush} disabled={pushBusy}>
                {pushBusy ? t('common.loading') : t('push.disable')}
              </button>
            ) : (
              <button type="button" className="btn-primary text-sm" onClick={enablePush} disabled={pushBusy}>
                {pushBusy ? t('common.loading') : t('push.enable')}
              </button>
            )}
          </div>
        </div>
      )}

      <div className="card mt-6 space-y-4">
        <h2 className="text-sm font-semibold text-ink-900 dark:text-slate-100">{t('profile.exportMyData')}</h2>
        <p className="text-sm text-ink-700/80 dark:text-slate-400">{t('profile.exportMyDataHint')}</p>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="btn-secondary text-sm"
            onClick={downloadMyData}
            disabled={!!dataBusy}
          >
            {dataBusy === 'export' ? t('common.loading') : t('profile.exportMyData')}
          </button>
          <button
            type="button"
            className="btn-danger text-sm"
            onClick={() => setDeactivateOpen(true)}
            disabled={!!dataBusy}
          >
            {t('profile.deactivateAccount')}
          </button>
        </div>
      </div>

      <ConfirmDialog
        open={deactivateOpen}
        title={t('profile.deactivateAccount')}
        message={t('profile.deactivateConfirm')}
        confirmLabel={t('profile.deactivateAccount')}
        onConfirm={confirmDeactivate}
        onCancel={() => {
          if (dataBusy === 'deactivate') return;
          setDeactivateOpen(false);
        }}
        busy={dataBusy === 'deactivate'}
      />
    </div>
  );
}
