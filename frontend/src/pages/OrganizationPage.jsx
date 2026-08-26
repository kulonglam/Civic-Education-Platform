import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useOrganization } from '../context/OrganizationContext';
import {
  auditService,
  billingService,
  notificationService,
  organizationService,
  notifyService,
} from '../lib/services';
import { extractError } from '../lib/api';
import { DEFAULT_PRIMARY_COLOR, normalizePrimaryColor } from '../lib/theme';
import { Alert, ConfirmDialog, PageHeader, Spinner } from '../components/ui';
import { TabList, TabPanel } from '../components/SettingsChrome';

const ORG_ROLES = ['member', 'moderator', 'content_manager', 'admin'];
const ORG_TABS = ['general', 'security', 'people', 'alerts'];

function OrganizationPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { organization, membership, isOrgAdmin, refresh } = useOrganization();
  const [members, setMembers] = useState([]);
  const [pendingInvites, setPendingInvites] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [form, setForm] = useState({
    name: '',
    tagline: '',
    logo_url: '',
    primary_color: DEFAULT_PRIMARY_COLOR,
    force_mfa_for_admins: false,
    audit_retention_days: 365,
    ip_allowlist_text: '',
  });
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('member');
  const [inviteDepartmentId, setInviteDepartmentId] = useState('');
  const [deptName, setDeptName] = useState('');
  const [bulkCsv, setBulkCsv] = useState('');
  const [bulkResult, setBulkResult] = useState(null);
  const [ssoForm, setSsoForm] = useState({
    enabled: false,
    issuer: '',
    client_id: '',
    client_secret: '',
    scopes: 'openid profile email',
    has_client_secret: false,
  });
  const [scimTokens, setScimTokens] = useState([]);
  const [scimTokenName, setScimTokenName] = useState('IdP provisioning');
  const [scimNewToken, setScimNewToken] = useState('');
  const [supportCases, setSupportCases] = useState([]);
  const [supportSubject, setSupportSubject] = useState('');
  const [supportBody, setSupportBody] = useState('');
  const [smsMessage, setSmsMessage] = useState('');
  const [announceTitle, setAnnounceTitle] = useState('');
  const [announceMessage, setAnnounceMessage] = useState('');
  const [announceBusy, setAnnounceBusy] = useState(false);
  const [targetedMessage, setTargetedMessage] = useState('');
  const [extraPhone, setExtraPhone] = useState('');
  const [selectedMemberIds, setSelectedMemberIds] = useState([]);
  const [smsHistory, setSmsHistory] = useState([]);
  const [whatsappMessage, setWhatsappMessage] = useState('');
  const [whatsappHistory, setWhatsappHistory] = useState([]);
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [leaveConfirmOpen, setLeaveConfirmOpen] = useState(false);
  const [leaving, setLeaving] = useState(false);
  const [orgTab, setOrgTab] = useState(() => {
    const tab = searchParams.get('tab');
    return ORG_TABS.includes(tab) ? tab : 'general';
  });

  const changeOrgTab = (tab) => {
    setOrgTab(tab);
    const next = new URLSearchParams(searchParams);
    if (tab === 'general') next.delete('tab');
    else next.set('tab', tab);
    setSearchParams(next, { replace: true });
  };

  useEffect(() => {
    const tab = searchParams.get('tab');
    const next = tab && ORG_TABS.includes(tab) ? tab : 'general';
    setOrgTab((prev) => (prev === next ? prev : next));
  }, [searchParams]);

  const roleLabel = (role) => {
    const map = {
      member: t('saas.roleMember'),
      admin: t('saas.roleAdmin'),
      content_manager: t('saas.roleContentManager'),
      moderator: t('saas.roleModerator'),
      owner: 'Owner',
    };
    return map[role] || role;
  };

  useEffect(() => {
    if (organization) {
      setForm({
        name: organization.name,
        tagline: organization.tagline,
        logo_url: organization.logo_url,
        primary_color: normalizePrimaryColor(organization.primary_color) || DEFAULT_PRIMARY_COLOR,
        force_mfa_for_admins: Boolean(organization.force_mfa_for_admins),
        audit_retention_days: organization.audit_retention_days ?? 365,
        ip_allowlist_text: (organization.ip_allowlist || []).join('\n'),
      });
    }
  }, [organization]);

  const loadScimAndSupport = async () => {
    if (!isOrgAdmin) return;
    try {
      const [tokens, cases] = await Promise.all([
        organizationService.scimTokens(),
        organizationService.supportCases(),
      ]);
      setScimTokens(Array.isArray(tokens.data) ? tokens.data : []);
      setSupportCases(Array.isArray(cases.data) ? cases.data : cases.data.results ?? []);
    } catch {
      setScimTokens([]);
      setSupportCases([]);
    }
  };
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
    try {
      const { data } = await notifyService.whatsappHistory();
      setWhatsappHistory(data.results ?? []);
    } catch {
      setWhatsappHistory([]);
    }
  };

  const loadDepartments = async () => {
    if (!isOrgAdmin) return;
    try {
      const { data } = await organizationService.departments();
      setDepartments(Array.isArray(data) ? data : data.results ?? []);
    } catch {
      setDepartments([]);
    }
  };

  const loadSso = async () => {
    if (!isOrgAdmin) return;
    try {
      const { data } = await organizationService.getSso();
      setSsoForm({
        enabled: Boolean(data.enabled),
        issuer: data.issuer || '',
        client_id: data.client_id || '',
        client_secret: '',
        scopes: data.scopes || 'openid profile email',
        has_client_secret: Boolean(data.has_client_secret),
      });
    } catch {
      /* SSO may require Enterprise plan */
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
        await loadDepartments();
        await loadSso();
        await loadScimAndSupport();
      } catch (err) {
        setError(extractError(err));
      } finally {
        setLoading(false);
      }
    })();
    // Intentionally re-load when admin role flips; loaders are stable for this page.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOrgAdmin]);

  const saveBranding = async (e) => {
    e.preventDefault();
    if (!isOrgAdmin) return;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const payload = {
        name: form.name,
        tagline: form.tagline,
        logo_url: form.logo_url,
        primary_color: form.primary_color,
        force_mfa_for_admins: form.force_mfa_for_admins,
        audit_retention_days: form.audit_retention_days,
        ip_allowlist: form.ip_allowlist_text
          .split(/[\n,]+/)
          .map((s) => s.trim())
          .filter(Boolean),
      };
      await organizationService.update(payload);
      await refresh();
      setSuccess(t('saas.orgSaved'));
    } catch (err) {
      setError(extractError(err));
    } finally {
      setSaving(false);
    }
  };

  const saveSso = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const payload = {
        enabled: ssoForm.enabled,
        issuer: ssoForm.issuer,
        client_id: ssoForm.client_id,
        scopes: ssoForm.scopes,
      };
      if (ssoForm.client_secret.trim()) {
        payload.client_secret = ssoForm.client_secret.trim();
      }
      const { data } = await organizationService.updateSso(payload);
      setSsoForm((prev) => ({
        ...prev,
        enabled: Boolean(data.enabled),
        issuer: data.issuer || '',
        client_id: data.client_id || '',
        client_secret: '',
        scopes: data.scopes || 'openid profile email',
        has_client_secret: Boolean(data.has_client_secret),
      }));
      setSuccess(t('saas.ssoSaved'));
    } catch (err) {
      setError(extractError(err));
    }
  };

  const addDepartment = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const { data } = await organizationService.createDepartment({ name: deptName.trim() });
      setDepartments((list) => [...list, data]);
      setDeptName('');
    } catch (err) {
      setError(extractError(err));
    }
  };

  const removeDepartment = async (id) => {
    setError('');
    try {
      await organizationService.deleteDepartment(id);
      setDepartments((list) => list.filter((d) => d.id !== id));
    } catch (err) {
      setError(extractError(err));
    }
  };

  const runBulkImport = async (dryRun) => {
    setError('');
    setSuccess('');
    setBulkResult(null);
    try {
      const lines = bulkCsv
        .trim()
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter(Boolean);
      if (lines.length === 0) {
        setError(t('saas.bulkImportHint'));
        return;
      }
      const header = lines[0].toLowerCase();
      const dataLines = header.includes('email') ? lines.slice(1) : lines;
      const rows = dataLines.map((line) => {
        const [email = '', first_name = '', last_name = '', role = 'member', department = ''] =
          line.split(',').map((part) => part.trim());
        return { email, first_name, last_name, role: role || 'member', department };
      });
      const { data } = await organizationService.bulkImport({
        rows,
        dry_run: dryRun,
        send_invites: true,
      });
      setBulkResult(data);
      if (!dryRun) {
        await loadMembers();
        await loadInvites();
        setSuccess(t('saas.bulkImportSubmit'));
      }
    } catch (err) {
      setError(extractError(err));
    }
  };

  const exportAudit = async () => {
    setError('');
    try {
      const response = await auditService.export({ format: 'csv' });
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'audit-log.csv';
      link.click();
      URL.revokeObjectURL(url);
      setSuccess(t('saas.exportAudit'));
    } catch (err) {
      setError(extractError(err));
    }
  };

  const downloadCompliancePack = async () => {
    setError('');
    try {
      const { data } = await organizationService.compliancePack();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'compliance-evidence-pack.json';
      link.click();
      URL.revokeObjectURL(url);
      setSuccess(t('saas.complianceDownloaded'));
    } catch (err) {
      setError(extractError(err));
    }
  };

  const createScimToken = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const { data } = await organizationService.createScimToken(scimTokenName);
      setScimNewToken(data.token || '');
      await loadScimAndSupport();
      setSuccess(t('saas.scimTokenCreated'));
    } catch (err) {
      setError(extractError(err));
    }
  };

  const revokeScimToken = async (id) => {
    try {
      await organizationService.revokeScimToken(id);
      await loadScimAndSupport();
    } catch (err) {
      setError(extractError(err));
    }
  };

  const openSupportCase = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await organizationService.createSupportCase({
        subject: supportSubject,
        body: supportBody,
        priority: 'normal',
      });
      setSupportSubject('');
      setSupportBody('');
      await loadScimAndSupport();
      setSuccess(t('saas.supportOpened'));
    } catch (err) {
      setError(extractError(err));
    }
  };

  const invite = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const { status, data } = await organizationService.invite(
        inviteEmail,
        inviteRole,
        inviteDepartmentId || null,
      );
      if (status === 202) {
        setPendingInvites((list) => [...list, data]);
        setSuccess(t('saas.inviteSent'));
      } else {
        setMembers((m) => [...m, data]);
        setSuccess(t('saas.memberInvited'));
      }
      setInviteEmail('');
      setInviteRole('member');
      setInviteDepartmentId('');
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

  const updateMemberRole = async (membershipId, role, departmentId) => {
    setError('');
    try {
      const { data } = await organizationService.updateMemberRole(
        membershipId,
        role,
        departmentId === undefined ? undefined : departmentId || null,
      );
      setMembers((list) => list.map((m) => (m.id === membershipId ? data : m)));
    } catch (err) {
      setError(extractError(err));
    }
  };

  const hasSsoPlan = Boolean(subscription?.plan?.features?.sso);

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

  const sendWhatsAppBroadcast = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      await notifyService.whatsappBroadcast(whatsappMessage);
      setWhatsappMessage('');
      setSuccess(t('whatsapp.broadcastQueued'));
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
        eyebrow={t('saas.orgEyebrow')}
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
          <p className="mt-1 text-sm text-ink-700 dark:text-slate-300">{t('roles.orgAdminPanelDesc')}</p>
        </div>
      )}

      {isOrgAdmin && (
        <div className="mb-6">
          <Link to="/categories/manage" className="text-sm font-semibold text-brand-700 hover:underline dark:text-brand-400">
            {t('categories.manageTitle')} →
          </Link>
        </div>
      )}

      {isOrgAdmin && (
        <TabList
          tabs={[
            { id: 'general', label: t('saas.tabGeneral') },
            { id: 'security', label: t('saas.tabSecurity') },
            { id: 'people', label: t('saas.tabPeople') },
            { id: 'alerts', label: t('saas.tabAlerts') },
          ]}
          active={orgTab}
          onChange={changeOrgTab}
        />
      )}

      {isOrgAdmin && (
        <TabPanel id="general" active={orgTab}>
        <form onSubmit={saveBranding} className="card mb-8 space-y-4">
          <h2 className="font-display text-xl font-semibold text-ink-900 dark:text-slate-100">{t('saas.branding')}</h2>
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
          <label className="flex items-center gap-2 text-sm text-ink-700 dark:text-slate-300">
            <input
              type="checkbox"
              checked={form.force_mfa_for_admins}
              onChange={(e) => setForm({ ...form, force_mfa_for_admins: e.target.checked })}
            />
            {t('saas.forceMfa')}
          </label>
          <div>
            <label className="label">{t('saas.auditRetention')}</label>
            <input
              className="input"
              type="number"
              min={30}
              max={3650}
              value={form.audit_retention_days}
              onChange={(e) =>
                setForm({ ...form, audit_retention_days: Number(e.target.value) || 365 })
              }
            />
          </div>
          <div>
            <label className="label">{t('saas.ipAllowlist')}</label>
            <textarea
              className="input min-h-[80px] font-mono text-xs"
              value={form.ip_allowlist_text}
              onChange={(e) => setForm({ ...form, ip_allowlist_text: e.target.value })}
              placeholder={'203.0.113.0/24\n198.51.100.10'}
            />
            <p className="mt-1 text-xs text-ink-700/60 dark:text-slate-400">{t('saas.ipAllowlistHint')}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? t('common.loading') : t('common.save')}
            </button>
            <button type="button" className="btn-secondary" onClick={exportAudit}>
              {t('saas.exportAudit')}
            </button>
            <button type="button" className="btn-secondary" onClick={downloadCompliancePack}>
              {t('saas.compliancePack')}
            </button>
          </div>
          <p className="text-xs text-ink-700/60 dark:text-slate-400">{t('saas.complianceDisclaimer')}</p>
        </form>
        </TabPanel>
      )}

      {isOrgAdmin && (
        <TabPanel id="security" active={orgTab}>
        <form onSubmit={saveSso} className="card mb-8 space-y-4">
          <h2 className="font-display text-xl font-semibold text-ink-900 dark:text-slate-100">{t('saas.ssoTitle')}</h2>
          <p className="text-sm text-ink-700/60 dark:text-slate-400">{t('saas.ssoSubtitle')}</p>
          {!hasSsoPlan && (
            <Alert kind="warning">{t('saas.upgradePlan')}</Alert>
          )}
          <label className="flex items-center gap-2 text-sm text-ink-700 dark:text-slate-300">
            <input
              type="checkbox"
              checked={ssoForm.enabled}
              onChange={(e) => setSsoForm({ ...ssoForm, enabled: e.target.checked })}
              disabled={!hasSsoPlan}
            />
            {t('saas.ssoEnabled')}
          </label>
          <div>
            <label className="label">{t('saas.ssoIssuer')}</label>
            <input
              className="input"
              value={ssoForm.issuer}
              onChange={(e) => setSsoForm({ ...ssoForm, issuer: e.target.value })}
              disabled={!hasSsoPlan}
              placeholder="https://login.microsoftonline.com/{tenant}/v2.0"
            />
          </div>
          <div>
            <label className="label">{t('saas.ssoClientId')}</label>
            <input
              className="input"
              value={ssoForm.client_id}
              onChange={(e) => setSsoForm({ ...ssoForm, client_id: e.target.value })}
              disabled={!hasSsoPlan}
            />
          </div>
          <div>
            <label className="label">{t('saas.ssoClientSecret')}</label>
            <input
              className="input"
              type="password"
              autoComplete="new-password"
              value={ssoForm.client_secret}
              onChange={(e) => setSsoForm({ ...ssoForm, client_secret: e.target.value })}
              disabled={!hasSsoPlan}
              placeholder={ssoForm.has_client_secret ? '••••••••' : ''}
            />
          </div>
          <div>
            <label className="label">{t('saas.ssoScopes')}</label>
            <input
              className="input"
              value={ssoForm.scopes}
              onChange={(e) => setSsoForm({ ...ssoForm, scopes: e.target.value })}
              disabled={!hasSsoPlan}
            />
          </div>
          <button type="submit" className="btn-primary" disabled={!hasSsoPlan}>
            {t('common.save')}
          </button>
        </form>

        <div className="card mb-8 space-y-4">
          <h2 className="font-display text-xl font-semibold text-ink-900 dark:text-slate-100">{t('saas.scimTitle')}</h2>
          <p className="text-sm text-ink-700/60 dark:text-slate-400">{t('saas.scimSubtitle')}</p>
          <p className="text-xs text-ink-700/60 dark:text-slate-400">
            {t('saas.scimEndpoint')}: <code className="rounded bg-ink-100 px-1 dark:bg-slate-900">/scim/v2/Users</code>
          </p>
          <form onSubmit={createScimToken} className="flex flex-wrap gap-2">
            <input
              className="input flex-1"
              value={scimTokenName}
              onChange={(e) => setScimTokenName(e.target.value)}
              placeholder={t('saas.scimTokenName')}
            />
            <button type="submit" className="btn-primary">{t('saas.scimCreateToken')}</button>
          </form>
          {scimNewToken && (
            <Alert kind="warning">
              <span className="break-all font-mono text-xs">{scimNewToken}</span>
            </Alert>
          )}
          <ul className="divide-y divide-ink-100 dark:divide-slate-700">
            {scimTokens.map((tok) => (
              <li key={tok.id} className="flex items-center justify-between py-2 text-sm">
                <span className="text-ink-900 dark:text-slate-100">
                  {tok.name} · {tok.token_prefix}… {!tok.is_active ? '(revoked)' : ''}
                </span>
                {tok.is_active && (
                  <button type="button" className="btn-secondary text-xs" onClick={() => revokeScimToken(tok.id)}>
                    {t('saas.scimRevoke')}
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>

        <div className="card mb-8 space-y-4">
          <h2 className="font-display text-xl font-semibold text-ink-900 dark:text-slate-100">{t('saas.supportTitle')}</h2>
          <p className="text-sm text-ink-700/70 dark:text-slate-400">{t('saas.supportSubtitle')}</p>
          <form onSubmit={openSupportCase} className="space-y-3">
            <input
              className="input"
              value={supportSubject}
              onChange={(e) => setSupportSubject(e.target.value)}
              placeholder={t('saas.supportSubject')}
              required
            />
            <textarea
              className="input min-h-[80px]"
              value={supportBody}
              onChange={(e) => setSupportBody(e.target.value)}
              placeholder={t('saas.supportBody')}
              required
            />
            <button type="submit" className="btn-primary">{t('saas.supportSubmit')}</button>
          </form>
          <ul className="divide-y divide-ink-100 dark:divide-slate-700">
            {supportCases.map((c) => (
              <li key={c.id} className="py-2 text-sm">
                <p className="font-medium text-ink-900 dark:text-slate-100">{c.subject}</p>
                <p className="text-xs capitalize text-ink-700/60 dark:text-slate-400">{c.status} · {c.priority}</p>
              </li>
            ))}
          </ul>
        </div>
        </TabPanel>
      )}

      {isOrgAdmin && (
        <TabPanel id="people" active={orgTab}>
        <div className="card mb-8 space-y-4">
          <h2 className="font-display text-xl font-semibold text-ink-900 dark:text-slate-100">{t('saas.departments')}</h2>
          <form onSubmit={addDepartment} className="flex flex-wrap gap-2">
            <input
              className="input flex-1"
              placeholder={t('saas.departmentName')}
              value={deptName}
              onChange={(e) => setDeptName(e.target.value)}
              required
            />
            <button type="submit" className="btn-primary">
              {t('saas.addDepartment')}
            </button>
          </form>
          <ul className="divide-y divide-ink-100 dark:divide-slate-700">
            {departments.map((d) => (
              <li key={d.id} className="flex items-center justify-between py-2 text-sm">
                <span className="text-ink-900 dark:text-slate-100">{d.name}</span>
                <button type="button" className="btn-secondary text-xs" onClick={() => removeDepartment(d.id)}>
                  {t('common.delete')}
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="card mb-8 space-y-4">
          <h2 className="font-display text-xl font-semibold text-ink-900 dark:text-slate-100">{t('saas.bulkImport')}</h2>
          <p className="text-sm text-ink-700/70 dark:text-slate-400">{t('saas.bulkImportHint')}</p>
          <textarea
            className="input min-h-[120px] font-mono text-xs"
            value={bulkCsv}
            onChange={(e) => setBulkCsv(e.target.value)}
            placeholder={'email,first_name,last_name,role,department\nuser@example.com,Ada,Okello,member,Education'}
          />
          <div className="flex flex-wrap gap-2">
            <button type="button" className="btn-secondary" onClick={() => runBulkImport(true)} disabled={!bulkCsv.trim()}>
              {t('saas.bulkImportDryRun')}
            </button>
            <button type="button" className="btn-primary" onClick={() => runBulkImport(false)} disabled={!bulkCsv.trim()}>
              {t('saas.bulkImportSubmit')}
            </button>
          </div>
          {bulkResult && (
            <pre className="max-h-48 overflow-auto rounded-xl bg-ink-50 p-3 text-xs dark:bg-slate-900 dark:text-slate-300">
              {JSON.stringify(bulkResult, null, 2)}
            </pre>
          )}
        </div>

      <div className="card mb-8">
        <h2 className="mb-4 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">{t('saas.members')}</h2>
        {isOrgAdmin && (
          <form onSubmit={invite} className="mb-6 flex flex-wrap gap-2">
            <input
              type="email"
              className="input flex-1 min-w-[12rem]"
              placeholder={t('saas.inviteEmail')}
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              required
            />
            <select
              className="input w-auto"
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value)}
            >
              {ORG_ROLES.map((role) => (
                <option key={role} value={role}>
                  {roleLabel(role)}
                </option>
              ))}
            </select>
            <select
              className="input w-auto"
              value={inviteDepartmentId}
              onChange={(e) => setInviteDepartmentId(e.target.value)}
            >
              <option value="">{t('saas.departments')}</option>
              {departments.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
            <button type="submit" className="btn-primary">{t('saas.invite')}</button>
          </form>
        )}

        {isOrgAdmin && pendingInvites.length > 0 && (
          <div className="mb-6 rounded-xl border border-amber-100 bg-amber-50 p-4 dark:border-amber-900/40 dark:bg-amber-950/30">
            <h3 className="mb-2 font-medium text-amber-900 dark:text-amber-200">{t('saas.pendingInvites')}</h3>
            <ul className="divide-y divide-amber-100 dark:divide-amber-900/40">
              {pendingInvites.map((inv) => (
                <li key={inv.id} className="flex items-center justify-between py-2 text-sm dark:text-slate-300">
                  <span>
                    {inv.email} · {roleLabel(inv.role)}
                    {inv.department?.name ? ` · ${inv.department.name}` : ''} · {t('saas.invitePending')}
                  </span>
                  <button type="button" className="btn-secondary text-xs" onClick={() => revokeInvite(inv.id)}>
                    {t('common.cancel')}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        <ul className="divide-y divide-ink-100 dark:divide-slate-700">
          {members.map((m) => (
            <li key={m.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
              <div>
                <p className="font-medium text-ink-900 dark:text-slate-100">{m.user_name || m.user_email}</p>
                <p className="text-sm text-ink-700/60 dark:text-slate-400">
                  {m.user_email}
                  {m.department?.name ? ` · ${m.department.name}` : ''}
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                {isOrgAdmin && m.role !== 'owner' && m.id !== membership?.id ? (
                  <>
                    <select
                      className="input w-auto text-sm"
                      value={m.role}
                      onChange={(e) => updateMemberRole(m.id, e.target.value, m.department?.id)}
                    >
                      {ORG_ROLES.map((role) => (
                        <option key={role} value={role}>
                          {roleLabel(role)}
                        </option>
                      ))}
                    </select>
                    <select
                      className="input w-auto text-sm"
                      value={m.department?.id || ''}
                      onChange={(e) => updateMemberRole(m.id, m.role, e.target.value || null)}
                    >
                      <option value="">{t('saas.departments')}</option>
                      {departments.map((d) => (
                        <option key={d.id} value={d.id}>
                          {d.name}
                        </option>
                      ))}
                    </select>
                  </>
                ) : (
                  <span className="text-sm capitalize text-ink-700/60 dark:text-slate-400">
                    {roleLabel(m.role)}
                  </span>
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
        </TabPanel>
      )}

      {!isOrgAdmin && (
      <div className="card mb-8">
        <h2 className="mb-4 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">{t('saas.members')}</h2>
        <ul className="divide-y divide-ink-100 dark:divide-slate-700">
          {members.map((m) => (
            <li key={m.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
              <div>
                <p className="font-medium text-ink-900 dark:text-slate-100">{m.user_name || m.user_email}</p>
                <p className="text-sm text-ink-700/60 dark:text-slate-400">
                  {m.user_email}
                  {m.department?.name ? ` · ${m.department.name}` : ''}
                </p>
              </div>
              <span className="text-sm capitalize text-ink-700/60 dark:text-slate-400">
                {roleLabel(m.role)}
              </span>
            </li>
          ))}
        </ul>
      </div>
      )}

      {isOrgAdmin && (
        <TabPanel id="alerts" active={orgTab}>
        <div className="card mb-8">
          <h2 className="mb-2 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">{t('announcements.title')}</h2>
          <p className="mb-4 text-sm text-ink-700/70 dark:text-slate-400">{t('announcements.subtitle')}</p>
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

        <div className="card mb-8">
          <h2 className="mb-2 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">{t('sms.alertsTitle')}</h2>
          <p className="mb-4 text-sm text-ink-700/70 dark:text-slate-400">{t('sms.alertsSubtitle')}</p>
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

              <div className="mt-8 border-t border-ink-100 pt-6 dark:border-slate-700">
                <h3 className="mb-2 font-medium text-ink-900 dark:text-slate-100">{t('sms.targetedTitle')}</h3>
                <p className="mb-4 text-sm text-ink-700/60 dark:text-slate-400">{t('sms.targetedSubtitle')}</p>
                <form onSubmit={sendTargeted} className="space-y-3">
                  {members.length > 0 && (
                    <div className="max-h-48 space-y-2 overflow-y-auto rounded-lg border border-ink-100 p-3 dark:border-slate-600 dark:bg-slate-900/40">
                      {members.map((m) => (
                        <label key={m.id} className="flex items-center gap-2 text-sm">
                          <input
                            type="checkbox"
                            checked={selectedMemberIds.includes(m.user)}
                            onChange={() => toggleMember(m.user)}
                            disabled={!m.user_phone}
                          />
                          <span className={m.user_phone ? 'text-ink-900 dark:text-slate-200' : 'text-ink-700/70 dark:text-slate-500'}>
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
                      placeholder="+256772123456"
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
                    <p className="text-xs text-ink-700/70 dark:text-slate-500">{t('sms.noPhoneMembers')}</p>
                  )}
                </form>
              </div>

              {smsHistory.length > 0 && (
                <div className="mt-6">
                  <h3 className="mb-2 font-medium text-ink-900 dark:text-slate-100">{t('sms.recentDeliveries')}</h3>
                  <ul className="divide-y divide-ink-100 text-sm dark:divide-slate-700">
                    {smsHistory.slice(0, 5).map((row) => (
                      <li key={row.id} className="py-2">
                        <p className="font-medium text-ink-900 dark:text-slate-100">{row.phone}</p>
                        <p className="line-clamp-1 text-ink-700/80 dark:text-slate-400">{row.message}</p>
                        <p className="text-xs capitalize text-ink-700/70 dark:text-slate-500">
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

        <div className="card mb-8">
          <h2 className="mb-2 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">{t('whatsapp.alertsTitle')}</h2>
          <p className="mb-4 text-sm text-ink-700/70 dark:text-slate-400">{t('whatsapp.alertsSubtitle')}</p>
          {!hasSmsPlan ? (
            <div className="rounded-lg border border-amber-100 bg-amber-50 p-4 dark:border-amber-900/40 dark:bg-amber-950/30">
              <Alert kind="warning">{t('sms.upgradeRequired')}</Alert>
              <Link to="/billing" className="btn-primary mt-4 inline-block">
                {t('saas.upgradePlan')}
              </Link>
            </div>
          ) : (
            <>
              <form onSubmit={sendWhatsAppBroadcast} className="space-y-3">
                <textarea
                  className="input min-h-[100px]"
                  placeholder={t('whatsapp.messagePlaceholder')}
                  value={whatsappMessage}
                  onChange={(e) => setWhatsappMessage(e.target.value)}
                  required
                  maxLength={1000}
                />
                <button type="submit" className="btn-primary" disabled={!whatsappMessage.trim()}>
                  {t('whatsapp.broadcast')}
                </button>
              </form>
              {whatsappHistory.length > 0 && (
                <div className="mt-6">
                  <h3 className="mb-2 font-medium text-ink-900 dark:text-slate-100">{t('whatsapp.recentDeliveries')}</h3>
                  <ul className="divide-y divide-ink-100 text-sm dark:divide-slate-700">
                    {whatsappHistory.slice(0, 5).map((row) => (
                      <li key={row.id} className="py-2">
                        <p className="font-medium text-ink-900 dark:text-slate-100">{row.phone}</p>
                        <p className="line-clamp-1 text-ink-700/80 dark:text-slate-400">{row.message}</p>
                        <p className="text-xs capitalize text-ink-700/70 dark:text-slate-500">
                          {row.status} · {row.direction}
                        </p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
        </TabPanel>
      )}

      {membership && (
        <div className="card mt-8 border-red-100 dark:border-red-900/40">
          <h2 className="mb-2 font-display text-xl font-semibold text-red-900 dark:text-red-300">{t('saas.leaveTitle')}</h2>
          <p className="mb-4 text-sm text-ink-700/70 dark:text-slate-400">{t('saas.leaveHint')}</p>
          <button type="button" className="btn-danger" onClick={() => setLeaveConfirmOpen(true)}>
            {t('saas.leaveOrganization')}
          </button>
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
