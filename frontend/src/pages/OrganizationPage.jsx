import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';
import { useOrganization } from '../context/OrganizationContext';
import { billingService, notificationService, organizationService, notifyService } from '../lib/services';
import { extractError } from '../lib/api';
import { DEFAULT_PRIMARY_COLOR, normalizePrimaryColor } from '../lib/theme';
import { Alert, ConfirmDialog, PageHeader, Spinner } from '../components/ui';

function OrganizationPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { organization, membership, isOrgAdmin, refresh } = useOrganization();
  const [members, setMembers] = useState([]);
  const [pendingInvites, setPendingInvites] = useState([]);
  const [form, setForm] = useState({
    name: '',
    tagline: '',
    logo_url: '',
    primary_color: DEFAULT_PRIMARY_COLOR,
  });
  const [inviteEmail, setInviteEmail] = useState('');
  const [smsMessage, setSmsMessage] = useState('');
  const [announceTitle, setAnnounceTitle] = useState('');
  const [announceMessage, setAnnounceMessage] = useState('');
  const [announceBusy, setAnnounceBusy] = useState(false);
  const [targetedMessage, setTargetedMessage] = useState('');
  const [extraPhone, setExtraPhone] = useState('');
  const [selectedMemberIds, setSelectedMemberIds] = useState([]);
  const [smsHistory, setSmsHistory] = useState([]);
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [leaveConfirmOpen, setLeaveConfirmOpen] = useState(false);
  const [leaving, setLeaving] = useState(false);

  useEffect(() => {
    if (organization) {
      setForm({
        name: organization.name,
        tagline: organization.tagline,
        logo_url: organization.logo_url,
        primary_color: normalizePrimaryColor(organization.primary_color) || DEFAULT_PRIMARY_COLOR,
      });
    }
  }, [organization]);

  const loadMembers = async () => {
    const { data } = await organizationService.members();
    setMembers(data.results ?? data);
  };

  const loadInvites = async () => {
    if (!isOrgAdmin) return;
    try {
      const { data } = await organizationService.pendingInvites();
      setPendingInvites(Array.isArray(data) ? data : data.results ?? []);
    } catch {
      setPendingInvites([]);
    }
  };

  const loadSubscription = async () => {
    if (!isOrgAdmin) return;
    try {
      const { data } = await billingService.subscription();
      setSubscription(data.subscription ?? null);
    } catch {
      setSubscription(null);
    }
  };

  const loadSmsHistory = async () => {
    if (!isOrgAdmin) return;
    try {
      const { data } = await notifyService.history();
      setSmsHistory(data.results ?? []);
    } catch {
      setSmsHistory([]);
    }
  };

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        await loadMembers();
        await loadInvites();
        await loadSubscription();
        await loadSmsHistory();
      } catch (err) {
        setError(extractError(err));
      } finally {
        setLoading(false);
      }
    })();
  }, [isOrgAdmin]);

  const saveBranding = async (e) => {
    e.preventDefault();
    if (!isOrgAdmin) return;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await organizationService.update(form);
      await refresh();
      setSuccess(t('saas.orgSaved'));
    } catch (err) {
      setError(extractError(err));
    } finally {
      setSaving(false);
    }
  };

  const invite = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const { status, data } = await organizationService.invite(inviteEmail);
      if (status === 202) {
        setPendingInvites((list) => [...list, data]);
        setSuccess(t('saas.inviteSent'));
      } else {
        setMembers((m) => [...m, data]);
        setSuccess(t('saas.memberInvited'));
      }
      setInviteEmail('');
    } catch (err) {
      setError(extractError(err));
    }
  };

  const revokeInvite = async (id) => {
    try {
      await organizationService.revokeInvite(id);
      setPendingInvites((list) => list.filter((i) => i.id !== id));
    } catch (err) {
      setError(extractError(err));
    }
  };

  const removeMember = async (id) => {
    try {
      await organizationService.removeMember(id);
      setMembers((m) => m.filter((x) => x.id !== id));
    } catch (err) {
      setError(extractError(err));
    }
  };

  const updateMemberRole = async (membershipId, role) => {
    setError('');
    try {
      const { data } = await organizationService.updateMemberRole(membershipId, role);
      setMembers((list) => list.map((m) => (m.id === membershipId ? data : m)));
    } catch (err) {
      setError(extractError(err));
    }
  };

  const leaveOrganization = async () => {
    setLeaving(true);
    setError('');
    setSuccess('');
    try {
      await organizationService.leave();
      setLeaveConfirmOpen(false);
      await refresh();
      setSuccess(t('saas.leaveSuccess'));
      navigate('/');
    } catch (err) {
      setError(extractError(err));
    } finally {
      setLeaving(false);
    }
  };

  const sendInAppAnnouncement = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setAnnounceBusy(true);
    try {
      await notificationService.broadcast({
        title: announceTitle,
        message: announceMessage,
        notification_type: 'announcement',
      });
      setAnnounceTitle('');
      setAnnounceMessage('');
      setSuccess(t('announcements.sent'));
    } catch (err) {
      setError(extractError(err));
    } finally {
      setAnnounceBusy(false);
    }
  };

  const sendBroadcast = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      await notifyService.broadcast(smsMessage);
      setSmsMessage('');
      setSuccess(t('sms.broadcastQueued'));
      await loadSmsHistory();
    } catch (err) {
      if (err?.response?.status === 402) {
        setError(t('sms.upgradeRequired'));
      } else {
        setError(extractError(err));
      }
    }
  };

  const hasSmsPlan = Boolean(subscription?.plan?.features?.sms_alerts);

  const toggleMember = (userId) => {
    setSelectedMemberIds((ids) =>
      ids.includes(userId) ? ids.filter((id) => id !== userId) : [...ids, userId],
    );
  };

  const sendTargeted = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    const phones = extraPhone.trim() ? [extraPhone.trim()] : [];
    if (selectedMemberIds.length === 0 && phones.length === 0) {
      setError(t('sms.selectRecipients'));
      return;
    }
    try {
      await notifyService.sendSms({
        message: targetedMessage,
        user_ids: selectedMemberIds,
        phones,
      });
      setTargetedMessage('');
      setExtraPhone('');
      setSelectedMemberIds([]);
      setSuccess(t('sms.targetedQueued'));
      await loadSmsHistory();
    } catch (err) {
      if (err?.response?.status === 402) {
        setError(t('sms.upgradeRequired'));
      } else {
        setError(extractError(err));
      }
    }
  };

  const membersWithPhone = members.filter((m) => m.user_phone);

  if (loading && !organization) return <Spinner />;

  return (
    <div>
      <PageHeader
        title={t('saas.orgTitle')}
        subtitle={organization ? `${organization.slug} · ${membership?.role ?? ''}` : ''}
      />
      {error && (
        <div className="mb-4">
          <Alert>{error}</Alert>
        </div>
      )}
      {success && (
        <div className="mb-4">
          <Alert kind="success">{success}</Alert>
        </div>
      )}

      {isOrgAdmin && (
        <div className="card mb-6 border-teal-100 bg-teal-50/60 dark:border-teal-900/40 dark:bg-teal-950/30">
          <h2 className="text-sm font-semibold text-teal-900 dark:text-teal-200">{t('roles.orgAdminPanelTitle')}</h2>
          <p className="mt-1 text-sm text-gray-700 dark:text-slate-300">{t('roles.orgAdminPanelDesc')}</p>
        </div>
      )}

      {isOrgAdmin && (
        <div className="mb-6">
          <Link to="/categories/manage" className="text-sm text-brand-600 hover:underline dark:text-brand-400">
            {t('categories.manageTitle')} →
          </Link>
        </div>
      )}

      {isOrgAdmin && (
        <form onSubmit={saveBranding} className="card mb-8 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">{t('saas.branding')}</h2>
          <div>
            <label className="label">{t('saas.orgName')}</label>
            <input
              className="input"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="label">{t('saas.tagline')}</label>
            <input
              className="input"
              value={form.tagline}
              onChange={(e) => setForm({ ...form, tagline: e.target.value })}
            />
          </div>
          <div>
            <label className="label">{t('saas.logoUrl')}</label>
            <input
              className="input"
              type="url"
              value={form.logo_url}
              onChange={(e) => setForm({ ...form, logo_url: e.target.value })}
            />
          </div>
          <div>
            <label className="label">{t('saas.primaryColor')}</label>
            <input
              className="input"
              type="color"
              value={form.primary_color}
              onChange={(e) => setForm({ ...form, primary_color: e.target.value })}
            />
          </div>
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? t('common.loading') : t('common.save')}
          </button>
        </form>
      )}

      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('saas.members')}</h2>
        {isOrgAdmin && (
          <form onSubmit={invite} className="mb-6 flex gap-2">
            <input
              type="email"
              className="input flex-1"
              placeholder={t('saas.inviteEmail')}
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              required
            />
            <button type="submit" className="btn-primary">{t('saas.invite')}</button>
          </form>
        )}

        {isOrgAdmin && pendingInvites.length > 0 && (
          <div className="mb-6 rounded-lg border border-amber-100 bg-amber-50 p-4 dark:border-amber-900/40 dark:bg-amber-950/30">
            <h3 className="mb-2 font-medium text-amber-900 dark:text-amber-200">{t('saas.pendingInvites')}</h3>
            <ul className="divide-y divide-amber-100 dark:divide-amber-900/40">
              {pendingInvites.map((inv) => (
                <li key={inv.id} className="flex items-center justify-between py-2 text-sm dark:text-slate-300">
                  <span>{inv.email} · {inv.role} · {t('saas.invitePending')}</span>
                  <button type="button" className="btn-secondary text-xs" onClick={() => revokeInvite(inv.id)}>
                    {t('common.cancel')}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        <ul className="divide-y divide-gray-100 dark:divide-slate-700">
          {members.map((m) => (
            <li key={m.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
              <div>
                <p className="font-medium text-gray-900 dark:text-slate-100">{m.user_name || m.user_email}</p>
                <p className="text-sm text-gray-500 dark:text-slate-400">{m.user_email}</p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                {isOrgAdmin && m.role !== 'owner' && m.id !== membership?.id ? (
                  <select
                    className="input w-auto text-sm"
                    value={m.role}
                    onChange={(e) => updateMemberRole(m.id, e.target.value)}
                  >
                    <option value="member">{t('saas.roleMember')}</option>
                    <option value="admin">{t('saas.roleAdmin')}</option>
                  </select>
                ) : (
                  <span className="text-sm capitalize text-gray-500 dark:text-slate-400">{m.role}</span>
                )}
                {isOrgAdmin && m.id !== membership?.id && m.role !== 'owner' && (
                  <button type="button" className="btn-secondary text-sm" onClick={() => removeMember(m.id)}>
                    {t('common.delete')}
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      </div>

      {membership && (
        <div className="card mt-8 border-red-100 dark:border-red-900/40">
          <h2 className="mb-2 text-lg font-semibold text-red-900 dark:text-red-300">{t('saas.leaveTitle')}</h2>
          <p className="mb-4 text-sm text-gray-600 dark:text-slate-400">{t('saas.leaveHint')}</p>
          <button type="button" className="btn-danger" onClick={() => setLeaveConfirmOpen(true)}>
            {t('saas.leaveOrganization')}
          </button>
        </div>
      )}

      {isOrgAdmin && (
        <div className="card mt-8">
          <h2 className="mb-2 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('announcements.title')}</h2>
          <p className="mb-4 text-sm text-gray-500 dark:text-slate-400">{t('announcements.subtitle')}</p>
          <form onSubmit={sendInAppAnnouncement} className="space-y-3">
            <div>
              <label className="label">{t('announcements.fieldTitle')}</label>
              <input
                className="input"
                value={announceTitle}
                onChange={(e) => setAnnounceTitle(e.target.value)}
                required
                maxLength={255}
              />
            </div>
            <textarea
              className="input min-h-[100px]"
              placeholder={t('announcements.messagePlaceholder')}
              value={announceMessage}
              onChange={(e) => setAnnounceMessage(e.target.value)}
              required
              maxLength={2000}
            />
            <button
              type="submit"
              className="btn-primary"
              disabled={!announceTitle.trim() || !announceMessage.trim() || announceBusy}
            >
              {announceBusy ? t('common.loading') : t('announcements.send')}
            </button>
          </form>
        </div>
      )}

      {isOrgAdmin && (
        <div className="card mt-8">
          <h2 className="mb-2 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('sms.alertsTitle')}</h2>
          <p className="mb-4 text-sm text-gray-500 dark:text-slate-400">{t('sms.alertsSubtitle')}</p>
          {!hasSmsPlan ? (
            <div className="rounded-lg border border-amber-100 bg-amber-50 p-4 dark:border-amber-900/40 dark:bg-amber-950/30">
              <Alert kind="warning">{t('sms.upgradeRequired')}</Alert>
              <Link to="/billing" className="btn-primary mt-4 inline-block">
                {t('saas.upgradePlan')}
              </Link>
            </div>
          ) : (
            <>
              <form onSubmit={sendBroadcast} className="space-y-3">
                <textarea
                  className="input min-h-[100px]"
                  placeholder={t('sms.messagePlaceholder')}
                  value={smsMessage}
                  onChange={(e) => setSmsMessage(e.target.value)}
                  required
                  maxLength={480}
                />
                <button type="submit" className="btn-primary" disabled={!smsMessage.trim()}>
                  {t('sms.broadcast')}
                </button>
              </form>

              <div className="mt-8 border-t border-gray-100 pt-6 dark:border-slate-700">
                <h3 className="mb-2 font-medium text-gray-900 dark:text-slate-100">{t('sms.targetedTitle')}</h3>
                <p className="mb-4 text-sm text-gray-500 dark:text-slate-400">{t('sms.targetedSubtitle')}</p>
                <form onSubmit={sendTargeted} className="space-y-3">
                  {members.length > 0 && (
                    <div className="max-h-48 space-y-2 overflow-y-auto rounded-lg border border-gray-100 p-3 dark:border-slate-600 dark:bg-slate-900/40">
                      {members.map((m) => (
                        <label key={m.id} className="flex items-center gap-2 text-sm">
                          <input
                            type="checkbox"
                            checked={selectedMemberIds.includes(m.user)}
                            onChange={() => toggleMember(m.user)}
                            disabled={!m.user_phone}
                          />
                          <span className={m.user_phone ? 'text-gray-900 dark:text-slate-200' : 'text-gray-400 dark:text-slate-500'}>
                            {m.user_name || m.user_email}
                            {m.user_phone ? ` · ${m.user_phone}` : ` · ${t('sms.noPhone')}`}
                          </span>
                        </label>
                      ))}
                    </div>
                  )}
                  <div>
                    <label className="label">{t('sms.extraPhone')}</label>
                    <input
                      className="input"
                      placeholder="+211922123456"
                      value={extraPhone}
                      onChange={(e) => setExtraPhone(e.target.value)}
                    />
                  </div>
                  <textarea
                    className="input min-h-[80px]"
                    placeholder={t('sms.messagePlaceholder')}
                    value={targetedMessage}
                    onChange={(e) => setTargetedMessage(e.target.value)}
                    required
                    maxLength={480}
                  />
                  <button
                    type="submit"
                    className="btn-secondary"
                    disabled={
                      !targetedMessage.trim() ||
                      (selectedMemberIds.length === 0 && !extraPhone.trim())
                    }
                  >
                    {t('sms.sendTargeted')}
                  </button>
                  {membersWithPhone.length === 0 && !extraPhone && (
                    <p className="text-xs text-gray-400 dark:text-slate-500">{t('sms.noPhoneMembers')}</p>
                  )}
                </form>
              </div>

              {smsHistory.length > 0 && (
                <div className="mt-6">
                  <h3 className="mb-2 font-medium text-gray-900 dark:text-slate-100">{t('sms.recentDeliveries')}</h3>
                  <ul className="divide-y divide-gray-100 text-sm dark:divide-slate-700">
                    {smsHistory.slice(0, 5).map((row) => (
                      <li key={row.id} className="py-2">
                        <p className="font-medium text-gray-900 dark:text-slate-100">{row.phone}</p>
                        <p className="line-clamp-1 text-gray-600 dark:text-slate-400">{row.message}</p>
                        <p className="text-xs capitalize text-gray-400 dark:text-slate-500">
                          {row.status} · {row.message_type}
                        </p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      )}

      <ConfirmDialog
        open={leaveConfirmOpen}
        title={t('saas.leaveOrganization')}
        message={t('saas.leaveConfirm')}
        confirmLabel={t('saas.leaveOrganization')}
        onConfirm={leaveOrganization}
        onCancel={() => {
          if (leaving) return;
          setLeaveConfirmOpen(false);
        }}
        busy={leaving}
      />
    </div>
  );
}

export { OrganizationPage };
