// @ts-nocheck
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { analyticsService, auditService, awarenessService, billingService, forumService, notificationService, notifyService, organizationService, securityService, userService } from '../lib/services';
import { ADMIN, EDITOR, MODERATOR, CITIZEN, SUPER_ADMIN, RECOMMENDED_ROLES } from '../lib/roles';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import { extractError } from '../lib/api';
import { Alert, PageHeader, Spinner } from '../components/ui';
import { formatDate } from '../lib/format';
import { AdminTabBar } from './admin/AdminTabBar';

function StatCard({ label, value }) {
  return (
    <div className="card dark:border-slate-700 dark:bg-slate-800">
      <p className="text-sm text-ink-700/60 dark:text-slate-400">{label}</p>
      <p className="mt-1 text-3xl font-bold text-ink-900 dark:text-slate-100">{value}</p>
    </div>
  );
}

const CONTENT_LINKS = [
  { to: '/articles/new', titleKey: 'admin.createLesson', hintKey: 'admin.createLessonHint' },
  { to: '/articles/manage', titleKey: 'admin.editLessons', hintKey: 'admin.editLessonsHint' },
  { to: '/categories/manage', titleKey: 'categories.manageTitle', hintKey: 'admin.manageCategoriesHint' },
  { to: '/media/new', titleKey: 'admin.uploadVideo', hintKey: 'admin.uploadVideoHint' },
  { to: '/media/manage', titleKey: 'admin.uploadDocuments', hintKey: 'admin.uploadDocumentsHint' },
  { to: '/quizzes/new', titleKey: 'admin.createQuiz', hintKey: 'admin.createQuizHint' },
  { to: '/courses/manage', titleKey: 'admin.manageCourses', hintKey: 'admin.manageCoursesHint' },
  { to: '/engage/manage', titleKey: 'admin.manageEngage', hintKey: 'admin.manageEngageHint' },
];

function pct(value) {
  if (value === null || value === undefined || value === '') return '—';
  return `${value}%`;
}

function AdminPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user: currentUser, hasRole, isPlatformAdmin, isSuperAdmin, startImpersonation } = useAuth();
  const { isOrgAdmin, isOrgContentManager, isOrgModerator } = useOrganization();
  const isAdmin = isPlatformAdmin();
  const superAdmin = isSuperAdmin();
  const canManageContent = hasRole('admin', 'editor') || isOrgContentManager;
  const canModerate = hasRole('admin', 'moderator') || isOrgModerator;
  const canManagePlatformUsers = hasRole('admin', 'moderator');
  const ASSIGNABLE_ROLES = superAdmin
    ? [CITIZEN, EDITOR, MODERATOR, ADMIN, SUPER_ADMIN]
    : [CITIZEN, EDITOR, MODERATOR];
  const [overview, setOverview] = useState(null);
  const [quizStats, setQuizStats] = useState([]);
  const [forumStats, setForumStats] = useState(null);
  const [pollOpinion, setPollOpinion] = useState(null);
  const [learningStats, setLearningStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [userActionError, setUserActionError] = useState('');
  const [pendingTopics, setPendingTopics] = useState([]);
  const [pendingComments, setPendingComments] = useState([]);
  const [forumReports, setForumReports] = useState([]);
  const [misinfoReports, setMisinfoReports] = useState([]);
  const [platformMessage, setPlatformMessage] = useState('');
  const [platformSmsBusy, setPlatformSmsBusy] = useState(false);
  const [platformWhatsApp, setPlatformWhatsApp] = useState('');
  const [platformWhatsAppBusy, setPlatformWhatsAppBusy] = useState(false);
  const [auditLogs, setAuditLogs] = useState([]);
  const [pushStats, setPushStats] = useState(null);
  const [pushCleanupBusy, setPushCleanupBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [platformOrgs, setPlatformOrgs] = useState([]);
  const [orgSearch, setOrgSearch] = useState('');
  const [orgBusyId, setOrgBusyId] = useState(null);
  const [usageSummary, setUsageSummary] = useState(null);
  const [securityEvents, setSecurityEvents] = useState([]);
  const [supportOrg, setSupportOrg] = useState(null);
  const [impersonateBusy, setImpersonateBusy] = useState(null);
  const [supportBusy, setSupportBusy] = useState(false);
  const [sloMetrics, setSloMetrics] = useState(null);
  const [platformCases, setPlatformCases] = useState([]);
  const [platformPlans, setPlatformPlans] = useState([]);
  const [planBusyId, setPlanBusyId] = useState(null);

  const loadModeration = () =>
    Promise.all([
      forumService
        .pending()
        .then((r) => {
          setPendingTopics(r.data.topics);
          setPendingComments(r.data.comments);
          setForumReports(r.data.reports ?? []);
        })
        .catch(() => {}),
      awarenessService
        .listReports({ status: 'pending' })
        .then((r) => setMisinfoReports(r.data.results ?? r.data ?? []))
        .catch(() => setMisinfoReports([])),
    ]);

  useEffect(() => {
    const tasks = [];
    if (canModerate) {
      tasks.push(loadModeration());
    }
    if (isAdmin) {
      tasks.push(
        analyticsService.overview().then((r) => setOverview(r.data)),
        analyticsService.quizzes().then((r) => setQuizStats(r.data)),
        analyticsService.forum().then((r) => setForumStats(r.data)),
        analyticsService.polls().then((r) => setPollOpinion(r.data)),
        analyticsService.learning().then((r) => setLearningStats(r.data)),
        notificationService.pushStats().then((r) => setPushStats(r.data)),
      );
    }
    if (superAdmin) {
      tasks.push(
        organizationService.platformOrgs().then((r) => setPlatformOrgs(r.data.results ?? r.data)),
        organizationService.platformUsage().then((r) => setUsageSummary(r.data)),
        securityService.events({ page_size: 40 }).then((r) => setSecurityEvents(r.data.results ?? [])),
        organizationService.platformSlo().then((r) => setSloMetrics(r.data)),
        organizationService.platformSupportCases().then((r) => setPlatformCases(r.data.results ?? r.data)),
        billingService.plans().then((r) => setPlatformPlans(r.data.results ?? r.data ?? [])),
      );
    }
    if (canManagePlatformUsers) {
      tasks.push(userService.list().then((r) => setUsers(r.data.results ?? r.data)));
      tasks.push(
        auditService.logs({ page_size: 50 }).then((r) => setAuditLogs(r.data.results ?? r.data)),
      );
    }
    Promise.allSettled(tasks).finally(() => setLoading(false));
  }, [isAdmin, superAdmin, canModerate, canManagePlatformUsers]);

  const viewOrgSupport = async (orgId) => {
    setSupportBusy(true);
    try {
      const { data } = await organizationService.platformOrgDetail(orgId);
      setSupportOrg(data);
    } catch (err) {
      toast.error(extractError(err));
    } finally {
      setSupportBusy(false);
    }
  };

  const impersonateMember = async (orgId, userId) => {
    setImpersonateBusy(userId);
    try {
      await startImpersonation(orgId, userId);
      navigate('/');
    } catch (err) {
      toast.error(extractError(err));
    } finally {
      setImpersonateBusy(null);
    }
  };

  const moderateTopic = async (id, approve) => {
    await forumService.moderateTopic(id, approve);
    loadModeration();
  };

  const moderateComment = async (id, approve) => {
    await forumService.moderateComment(id, approve);
    loadModeration();
  };

  const reviewForumReport = async (id, status) => {
    try {
      await forumService.reviewReport(id, { status });
      await loadModeration();
    } catch (err) {
      toast.error(extractError(err));
    }
  };

  const reviewMisinfoReport = async (id, status) => {
    try {
      await awarenessService.reviewReport(id, { status });
      await loadModeration();
    } catch (err) {
      toast.error(extractError(err));
    }
  };

  const suspendUser = async (userId) => {
    setUserActionError('');
    try {
      await userService.suspend(userId);
      const { data } = await userService.list();
      setUsers(data.results ?? data);
    } catch (err) {
      setUserActionError(extractError(err));
    }
  };

  const unsuspendUser = async (userId) => {
    setUserActionError('');
    try {
      await userService.unsuspend(userId);
      const { data } = await userService.list();
      setUsers(data.results ?? data);
    } catch (err) {
      setUserActionError(extractError(err));
    }
  };

  const updateUserRole = async (userId, role) => {
    setUserActionError('');
    try {
      const { data } = await userService.updateRole(userId, role);
      setUsers((list) => list.map((u) => (u.id === userId ? data : u)));
    } catch (err) {
      setUserActionError(extractError(err));
    }
  };

  const sendPlatformAlert = async (e) => {
    e.preventDefault();
    setPlatformSmsBusy(true);
    try {
      const { data } = await notifyService.platformBroadcast(platformMessage);
      setPlatformMessage('');
      toast.success(data.message || t('admin.civicSmsQueued'));
    } catch (err) {
      toast.error(extractError(err));
    } finally {
      setPlatformSmsBusy(false);
    }
  };

  const sendPlatformWhatsApp = async (e) => {
    e.preventDefault();
    setPlatformWhatsAppBusy(true);
    try {
      const { data } = await notifyService.platformWhatsAppBroadcast(platformWhatsApp);
      setPlatformWhatsApp('');
      toast.success(data.message || t('admin.civicWhatsAppQueued'));
    } catch (err) {
      toast.error(extractError(err));
    } finally {
      setPlatformWhatsAppBusy(false);
    }
  };

  const cleanupPushSubscriptions = async () => {
    setPushCleanupBusy(true);
    try {
      const { data } = await notificationService.pushCleanup();
      toast.success(data.message);
      const stats = await notificationService.pushStats();
      setPushStats(stats.data);
    } catch (err) {
      toast.error(extractError(err));
    } finally {
      setPushCleanupBusy(false);
    }
  };

  const searchPlatformOrgs = async (search = orgSearch) => {
    try {
      const { data } = await organizationService.platformOrgs({ search: search || undefined });
      setPlatformOrgs(data.results ?? data);
    } catch (err) {
      toast.error(extractError(err));
    }
  };

  const toggleOrgActive = async (org) => {
    setOrgBusyId(org.id);
    try {
      const { data } = await organizationService.setOrgActive(org.id, !org.is_active);
      setPlatformOrgs((list) => list.map((o) => (o.id === org.id ? { ...o, ...data } : o)));
    } catch (err) {
      toast.error(extractError(err));
    } finally {
      setOrgBusyId(null);
    }
  };

  const assignOrgPlan = async (org, planCode) => {
    if (!planCode || planCode === org.plan_code) return;
    setPlanBusyId(org.id);
    try {
      const { data } = await organizationService.assignOrgPlan(org.id, planCode);
      setPlatformOrgs((list) => list.map((row) => (row.id === org.id ? { ...row, ...data } : row)));
      toast.success(t('admin.planAssigned'));
    } catch (err) {
      toast.error(extractError(err));
    } finally {
      setPlanBusyId(null);
    }
  };

  const adminTabs = [
    canManageContent && { id: 'content', label: t('admin.tabContent') },
    isAdmin && { id: 'overview', label: t('admin.tabOverview') },
    superAdmin && { id: 'orgs', label: t('admin.tabOrgs') },
    canManagePlatformUsers && { id: 'people', label: t('admin.tabPeople') },
    (canModerate || superAdmin) && { id: 'trust', label: t('admin.tabTrust') },
    superAdmin && { id: 'broadcast', label: t('admin.tabBroadcast') },
  ].filter(Boolean);
  const [tab, setTab] = useState(
    isAdmin ? 'overview' : canManageContent ? 'content' : 'trust',
  );
  const activeTab = adminTabs.some((item) => item.id === tab) ? tab : adminTabs[0]?.id;

  if (loading) return <Spinner />;


  return (
    <div className="space-y-10">
      <PageHeader
        title={
          isAdmin
            ? t('admin.platformTitle')
            : canManageContent && !canModerate
              ? t('admin.contentTitle')
              : t('admin.moderationTitle')
        }
        subtitle={
          isAdmin
            ? t('admin.platformSubtitle')
            : canManageContent && !canModerate
              ? t('admin.contentSubtitle')
              : t('admin.moderationSubtitle')
        }
      />

      {adminTabs.length > 1 && (
        <AdminTabBar
          label={t('admin.tablistLabel')}
          tabs={adminTabs}
          value={activeTab}
          onChange={setTab}
        />
      )}

      <div className="card border-brand-100 bg-brand-50/60 dark:border-brand-900/40 dark:bg-brand-950/30">
        <h2 className="text-sm font-semibold text-brand-900 dark:text-brand-200">{t('roles.modelTitle')}</h2>
        <p className="mt-1 text-sm text-ink-700/80 dark:text-slate-400">{t('roles.modelHint')}</p>
        <div className="mt-3 overflow-x-auto rounded-lg border border-brand-100 dark:border-brand-900/40">
          <table className="min-w-full text-sm">
            <thead className="bg-white/70 text-left text-ink-700/60 dark:bg-slate-900/40 dark:text-slate-400">
              <tr>
                <th className="px-3 py-2 font-medium">{t('roles.roleColumn')}</th>
                <th className="px-3 py-2 font-medium">{t('roles.permissionsColumn')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-brand-100/80 bg-white/50 dark:divide-slate-700 dark:bg-slate-900/20">
              {RECOMMENDED_ROLES.map((row) => (
                <tr key={row.key}>
                  <td className="px-3 py-2 font-medium text-ink-900 dark:text-slate-100">
                    {t(`admin.roles.${row.key}`)}
                  </td>
                  <td className="px-3 py-2 text-ink-700 dark:text-slate-300">{t(`roles.${row.permKey}`)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-sm text-ink-700/80 dark:text-slate-400">
          <strong>{t('roles.orgRole')}:</strong> {t('roles.orgRoleDesc')}
        </p>
        {!isAdmin && canModerate && (
          <p className="mt-3 text-sm text-ink-700/80 dark:text-slate-400">{t('admin.moderationPanelDesc')}</p>
        )}
        {!isAdmin && canManageContent && (
          <p className="mt-3 text-sm text-ink-700/80 dark:text-slate-400">{t('admin.contentPanelDesc')}</p>
        )}
      </div>

      {activeTab === 'content' && canManageContent && (
        <section>
          <h2 className="mb-2 text-lg font-semibold text-ink-900 dark:text-slate-100">{t('admin.contentManagement')}</h2>
          <p className="mb-4 text-sm text-ink-700/60 dark:text-slate-400">{t('admin.contentManagementHint')}</p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {CONTENT_LINKS.map((item) => (
              <Link
                key={item.to}
                to={item.to}
                className="card block transition hover:-translate-y-0.5 hover:shadow-lift dark:border-slate-700 dark:bg-slate-800"
              >
                <h3 className="font-semibold text-ink-900 dark:text-slate-100">{t(item.titleKey)}</h3>
                <p className="mt-1 text-sm text-ink-700/60 dark:text-slate-400">{t(item.hintKey)}</p>
              </Link>
            ))}
          </div>
          <p className="mt-3 text-sm text-ink-700/60 dark:text-slate-400">{t('admin.translateHint')}</p>
          {isOrgAdmin && !isAdmin && (
            <p className="mt-2 text-sm text-ink-700/60 dark:text-slate-400">
              <Link to="/dashboard" className="font-semibold text-brand-700 hover:underline dark:text-brand-400">
                {t('nav.dashboard')}
              </Link>
              {' — '}
              {t('admin.orgAnalyticsHint')}
            </p>
          )}
        </section>
      )}

      {activeTab === 'overview' && isAdmin && overview && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-ink-900 dark:text-slate-100">{t('admin.overview')}</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label={t('admin.totalUsers')} value={overview.total_users} />
            <StatCard label={t('admin.activeUsers')} value={overview.active_users_30d} />
            <StatCard label={t('admin.articlesPublished')} value={overview.articles_published} />
            <StatCard label={t('admin.quizCompletions')} value={overview.quiz_completions} />
            <StatCard label={t('admin.lessonCompletionRate')} value={pct(overview.lesson_completion_rate)} />
            <StatCard label={t('admin.mediaCompletionRate')} value={pct(overview.media_completion_rate)} />
            <StatCard label={t('admin.memberCompletionRate')} value={pct(overview.member_completion_rate)} />
          </div>
        </section>
      )}

      {activeTab === 'orgs' && superAdmin && (
        <section>
          <h2 className="mb-2 text-lg font-semibold text-ink-900 dark:text-slate-100">{t('admin.platformOrgs')}</h2>
          <p className="mb-4 text-sm text-ink-700/60 dark:text-slate-400">{t('admin.platformOrgsSubtitle')}</p>
          <form
            className="mb-4 flex flex-wrap gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              searchPlatformOrgs();
            }}
          >
            <input
              className="input max-w-md flex-1"
              placeholder={t('admin.searchOrgs')}
              value={orgSearch}
              onChange={(e) => setOrgSearch(e.target.value)}
            />
            <button type="submit" className="btn-secondary">
              {t('common.search')}
            </button>
          </form>
          <div className="overflow-x-auto rounded-xl border border-ink-100 bg-white dark:border-slate-700 dark:bg-slate-800">
            <table className="min-w-full text-sm">
              <thead className="bg-ink-50 text-left text-ink-700/60 dark:bg-slate-700/50 dark:text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-medium">{t('saas.orgName')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.plan')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.membersCount')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.accountStatus')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.actions')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-100 dark:divide-slate-700">
                {platformOrgs.map((org) => (
                  <tr key={org.id} className="dark:hover:bg-slate-700/30">
                    <td className="px-4 py-3">
                      <p className="font-medium text-ink-900 dark:text-slate-100">{org.name}</p>
                      <p className="text-xs text-ink-700/60 dark:text-slate-400">{org.slug}</p>
                    </td>
                    <td className="px-4 py-3 dark:text-slate-300">{org.plan_code || '—'}</td>
                    <td className="px-4 py-3 dark:text-slate-300">{org.member_count ?? '—'}</td>
                    <td className="px-4 py-3">
                      {org.is_active ? (
                        <span className="badge bg-green-100 text-green-700">{t('admin.active')}</span>
                      ) : (
                        <span className="badge bg-ink-100 text-ink-700/80">{t('admin.inactive')}</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-2">
                        <button
                          type="button"
                          className="btn-secondary text-xs"
                          disabled={supportBusy}
                          onClick={() => viewOrgSupport(org.id)}
                        >
                          {t('admin.viewSupport')}
                        </button>
                        <button
                          type="button"
                          className={org.is_active ? 'btn-danger text-xs' : 'btn-primary text-xs'}
                          disabled={orgBusyId === org.id}
                          onClick={() => toggleOrgActive(org)}
                        >
                          {org.is_active ? t('admin.deactivate') : t('admin.activate')}
                        </button>
                        {platformPlans.length > 0 && (
                          <select
                            className="input max-w-[8rem] py-1 text-xs"
                            value={org.plan_code || ''}
                            disabled={planBusyId === org.id}
                            onChange={(e) => assignOrgPlan(org, e.target.value)}
                            aria-label={t('admin.assignPlan')}
                          >
                            <option value="" disabled>
                              {t('admin.assignPlan')}
                            </option>
                            {platformPlans.map((plan) => (
                              <option key={plan.code} value={plan.code}>
                                {plan.name}
                              </option>
                            ))}
                          </select>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {activeTab === 'orgs' && superAdmin && supportOrg && (
        <section className="card">
          <div className="mb-3 flex items-center justify-between gap-2">
            <h2 className="text-lg font-semibold text-ink-900 dark:text-slate-100">
              {t('admin.supportView')}: {supportOrg.name}
            </h2>
            <button type="button" className="btn-secondary text-xs" onClick={() => setSupportOrg(null)}>
              {t('common.close')}
            </button>
          </div>
          <p className="mb-4 text-sm text-ink-700/60 dark:text-slate-400">{t('admin.supportViewHint')}</p>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label={t('admin.membersCount')} value={supportOrg.member_count} />
            <StatCard label={t('admin.plan')} value={supportOrg.plan_code || '—'} />
            <StatCard label={t('dashboard.publishedArticles')} value={supportOrg.published_articles} />
            <StatCard label={t('dashboard.quizAttempts')} value={supportOrg.quiz_attempts} />
            <StatCard label={t('dashboard.certificates')} value={supportOrg.certificates_issued} />
            <StatCard label={t('admin.activeLearners')} value={supportOrg.active_learners_30d} />
            <StatCard label={t('saas.departments')} value={supportOrg.department_count} />
            <StatCard label={t('admin.controlledDocs')} value={supportOrg.controlled_documents} />
          </div>
          {supportOrg.members?.length > 0 && (
            <div className="mt-6 overflow-x-auto rounded-xl border border-ink-100 dark:border-slate-700">
              <table className="min-w-full text-sm">
                <thead className="bg-ink-50 text-left text-ink-700/60 dark:bg-slate-700/50 dark:text-slate-400">
                  <tr>
                    <th className="px-4 py-3 font-medium">{t('saas.members')}</th>
                    <th className="px-4 py-3 font-medium">{t('admin.actions')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-ink-100 dark:divide-slate-700">
                  {supportOrg.members.map((member) => (
                    <tr key={member.user_id}>
                      <td className="px-4 py-3">
                        <p className="font-medium text-ink-900 dark:text-slate-100">{member.full_name}</p>
                        <p className="text-xs text-ink-700/60 dark:text-slate-400">{member.email}</p>
                      </td>
                      <td className="px-4 py-3">
                        <button
                          type="button"
                          className="btn-secondary text-xs"
                          disabled={!member.can_impersonate || impersonateBusy === member.user_id}
                          onClick={() => impersonateMember(supportOrg.id, member.user_id)}
                        >
                          {t('admin.impersonate')}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {activeTab === 'orgs' && superAdmin && usageSummary?.totals && (
        <section>
          <h2 className="mb-2 text-lg font-semibold text-ink-900 dark:text-slate-100">{t('admin.usageSummary')}</h2>
          <p className="mb-4 text-sm text-ink-700/60 dark:text-slate-400">{t('admin.usageSummarySubtitle')}</p>
          <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label={t('admin.platformOrgs')} value={usageSummary.totals.organizations} />
            <StatCard label={t('admin.membersCount')} value={usageSummary.totals.members} />
            <StatCard label={t('dashboard.quizAttempts')} value={usageSummary.totals.quiz_attempts} />
            <StatCard label={t('admin.activeLearners')} value={usageSummary.totals.active_learners_30d} />
          </div>
        </section>
      )}

      {activeTab === 'orgs' && superAdmin && sloMetrics && (
        <section>
          <h2 className="mb-2 text-lg font-semibold text-ink-900 dark:text-slate-100">SLO status</h2>
          <p className="mb-4 text-sm text-ink-700/60 dark:text-slate-400">
            24h auth success and security-event snapshot ({sloMetrics.status})
          </p>
          <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              label="Auth success %"
              value={sloMetrics.observed?.auth_success_rate_percent ?? '—'}
            />
            <StatCard label="Security events" value={sloMetrics.observed?.security_events_24h ?? 0} />
            <StatCard label="Open support cases" value={sloMetrics.observed?.open_support_cases ?? 0} />
            <StatCard label="Status" value={sloMetrics.status} />
          </div>
          {platformCases.length > 0 && (
            <ul className="mb-6 divide-y divide-ink-100 rounded-xl border border-ink-100 bg-white text-sm dark:divide-slate-700 dark:border-slate-700 dark:bg-slate-800">
              {platformCases.slice(0, 8).map((c) => (
                <li key={c.id} className="flex flex-wrap items-center justify-between gap-2 px-4 py-3">
                  <div>
                    <p className="font-medium text-ink-900 dark:text-slate-100">{c.subject}</p>
                    <p className="text-xs text-ink-700/60 dark:text-slate-400">
                      {c.organization_name} · {c.status} · {c.priority}
                    </p>
                  </div>
                  {c.status !== 'resolved' && c.status !== 'closed' && (
                    <button
                      type="button"
                      className="btn-secondary text-xs"
                      onClick={async () => {
                        try {
                          await organizationService.updatePlatformSupportCase(c.id, {
                            status: 'resolved',
                            assignee_notes: 'Resolved by platform admin',
                          });
                          const { data } = await organizationService.platformSupportCases();
                          setPlatformCases(data.results ?? data);
                          toast.success('Case resolved');
                        } catch (err) {
                          toast.error(extractError(err));
                        }
                      }}
                    >
                      Resolve
                    </button>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>
      )}

      {activeTab === 'trust' && superAdmin && securityEvents.length > 0 && (
        <section>
          <h2 className="mb-2 text-lg font-semibold text-ink-900 dark:text-slate-100">{t('admin.securityEvents')}</h2>
          <p className="mb-4 text-sm text-ink-700/60 dark:text-slate-400">{t('admin.securityEventsSubtitle')}</p>
          <div className="overflow-x-auto rounded-xl border border-ink-100 bg-white dark:border-slate-700 dark:bg-slate-800">
            <table className="min-w-full text-sm">
              <thead className="bg-ink-50 text-left text-ink-700/60 dark:bg-slate-700/50 dark:text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-medium">{t('audit.when')}</th>
                  <th className="px-4 py-3 font-medium">{t('audit.type')}</th>
                  <th className="px-4 py-3 font-medium">{t('audit.user')}</th>
                  <th className="px-4 py-3 font-medium">IP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-100 dark:divide-slate-700">
                {securityEvents.map((ev) => (
                  <tr key={ev.id} className="dark:hover:bg-slate-700/30">
                    <td className="px-4 py-3 whitespace-nowrap text-ink-700/60 dark:text-slate-400">
                      {formatDate(ev.created_at)}
                    </td>
                    <td className="px-4 py-3 dark:text-slate-300">{ev.event_type}</td>
                    <td className="px-4 py-3 dark:text-slate-300">{ev.user_email || '—'}</td>
                    <td className="px-4 py-3 dark:text-slate-400">{ev.ip_address || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {activeTab === 'overview' && isAdmin && pushStats && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-ink-900 dark:text-slate-100">{t('admin.pushTitle')}</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label={t('admin.pushSubscriptions')} value={pushStats.total_subscriptions} />
            <StatCard label={t('admin.pushUsers')} value={pushStats.users_with_push} />
            <StatCard label={t('admin.pushInactiveUsers')} value={pushStats.inactive_user_subscriptions} />
            <StatCard label={t('admin.activeUsers')} value={pushStats.total_users} />
          </div>
          <button
            type="button"
            className="btn-secondary mt-4 text-sm"
            onClick={cleanupPushSubscriptions}
            disabled={pushCleanupBusy}
          >
            {pushCleanupBusy ? t('common.loading') : t('admin.pushCleanup')}
          </button>
        </section>
      )}

      {activeTab === 'overview' && isAdmin && forumStats && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-ink-900 dark:text-slate-100">{t('admin.forumEngagement')}</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label={t('admin.totalTopics')} value={forumStats.total_topics} />
            <StatCard label={t('admin.totalComments')} value={forumStats.total_comments} />
            <StatCard label={t('admin.pendingTopics')} value={forumStats.pending_topics} />
            <StatCard label={t('admin.pendingComments')} value={forumStats.pending_comments} />
          </div>
        </section>
      )}

      {activeTab === 'overview' && isAdmin && pollOpinion && (
        <section>
          <h2 className="mb-2 text-lg font-semibold text-ink-900 dark:text-slate-100">{t('admin.pollOpinion')}</h2>
          <p className="mb-4 text-sm text-ink-700/60 dark:text-slate-400">{t('admin.pollOpinionHint')}</p>
          <div className="mb-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label={t('admin.totalPolls')} value={pollOpinion.total_polls} />
            <StatCard label={t('admin.totalPollResponses')} value={pollOpinion.total_responses} />
          </div>
          <div className="space-y-4">
            {(pollOpinion.polls ?? []).map((poll) => (
              <div key={poll.id} className="card space-y-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="badge bg-brand-50 text-brand-800 dark:bg-brand-900/30 dark:text-brand-200">
                    {t(`engage.kind_${poll.kind || 'community'}`)}
                  </span>
                  <span className="text-xs text-ink-700/60 dark:text-slate-400">
                    {t('engage.totalResponses', { count: poll.total_votes })}
                  </span>
                </div>
                <h3 className="font-semibold text-ink-900 dark:text-slate-100">{poll.question}</h3>
                <ul className="space-y-2">
                  {(poll.options ?? []).map((option) => (
                    <li key={option.id}>
                      <div className="mb-1 flex justify-between text-sm text-ink-700 dark:text-slate-300">
                        <span>{option.label}</span>
                        <span>{option.percent}%</span>
                      </div>
                      <div className="h-1.5 overflow-hidden rounded-full bg-ink-100 dark:bg-slate-700">
                        <div className="h-full bg-brand-600" style={{ width: `${option.percent || 0}%` }} />
                      </div>
                    </li>
                  ))}
                </ul>
                {poll.demographics_available ? (
                  <div className="grid gap-4 sm:grid-cols-2">
                    <div>
                      <h4 className="text-xs font-semibold uppercase tracking-wide text-ink-700/60 dark:text-slate-400">
                        {t('admin.regionalTrends')}
                      </h4>
                      <ul className="mt-2 space-y-1 text-sm text-ink-700 dark:text-slate-300">
                        {(poll.regions ?? []).map((row) => (
                          <li key={row.key} className="flex justify-between gap-3">
                            <span>{t(`admin.demo_${row.key}`, { defaultValue: t(`profile.region_${row.key}`, { defaultValue: row.key }) })}</span>
                            <span>{row.count}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="text-xs font-semibold uppercase tracking-wide text-ink-700/60 dark:text-slate-400">
                        {t('admin.demographicSummary')}
                      </h4>
                      <ul className="mt-2 space-y-1 text-sm text-ink-700 dark:text-slate-300">
                        {(poll.age_bands ?? []).map((row) => (
                          <li key={row.key} className="flex justify-between gap-3">
                            <span>{t(`admin.demo_${row.key}`, { defaultValue: t(`profile.age_${row.key}`, { defaultValue: row.key }) })}</span>
                            <span>{row.count}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-ink-700/60 dark:text-slate-400">{t('admin.pollDemographicsHidden')}</p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {activeTab === 'overview' && isAdmin && quizStats.length > 0 && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-ink-900 dark:text-slate-100">{t('admin.quizPerformance')}</h2>
          <div className="overflow-x-auto rounded-xl border border-ink-100 bg-white dark:border-slate-700 dark:bg-slate-800">
            <table className="min-w-full text-sm">
              <thead className="bg-ink-50 text-left text-ink-700/60 dark:bg-slate-700/50 dark:text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-medium">{t('quizzes.title')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.attempts')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.passRate')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.avgScore')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-100 dark:divide-slate-700">
                {quizStats.map((q) => (
                  <tr key={q.quiz_id} className="dark:hover:bg-slate-700/30">
                    <td className="px-4 py-3 font-medium text-ink-900 dark:text-slate-100">{q.title}</td>
                    <td className="px-4 py-3 dark:text-slate-300">{q.attempt_count}</td>
                    <td className="px-4 py-3 dark:text-slate-300">{q.pass_rate}%</td>
                    <td className="px-4 py-3 dark:text-slate-300">{q.avg_score}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {activeTab === 'overview' && isAdmin && learningStats && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-ink-900 dark:text-slate-100">{t('admin.learningInsights')}</h2>
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="card">
              <h3 className="mb-3 font-medium text-ink-900 dark:text-slate-100">{t('admin.articlesByCategory')}</h3>
              <ul className="divide-y divide-ink-100 text-sm dark:divide-slate-700">
                {(learningStats.articles_by_category ?? []).map((row) => (
                  <li key={row.slug} className="flex justify-between py-2 dark:text-slate-300">
                    <span>{row.category}</span>
                    <span className="font-medium">{row.article_count}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="card">
              <h3 className="mb-3 font-medium text-ink-900 dark:text-slate-100">{t('admin.popularLessons')}</h3>
              {(learningStats.popular_lessons ?? []).length === 0 ? (
                <p className="text-sm text-ink-700/60 dark:text-slate-400">{t('admin.noPopularLessons')}</p>
              ) : (
                <ul className="divide-y divide-ink-100 text-sm dark:divide-slate-700">
                  {(learningStats.popular_lessons ?? []).map((row) => (
                    <li key={row.id} className="flex justify-between gap-3 py-2 dark:text-slate-300">
                      <Link to={`/articles/${row.id}`} className="font-medium text-brand-700 hover:underline dark:text-brand-400">
                        {row.title}
                      </Link>
                      <span className="shrink-0 text-ink-700/60 dark:text-slate-400">
                        {t('admin.lessonStats', { completions: row.completions, views: row.views })}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="card">
              <h3 className="mb-3 font-medium text-ink-900 dark:text-slate-100">{t('admin.languagesUsed')}</h3>
              <ul className="divide-y divide-ink-100 text-sm dark:divide-slate-700">
                {(learningStats.languages ?? []).map((row) => (
                  <li key={row.key} className="flex justify-between py-2 dark:text-slate-300">
                    <span>{t(`admin.lang_${row.key}`, { defaultValue: row.key })}</span>
                    <span className="font-medium">{row.count}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="card">
              <h3 className="mb-3 font-medium text-ink-900 dark:text-slate-100">{t('admin.regionalEngagement')}</h3>
              {learningStats.regional_engagement?.demographics_available ? (
                <ul className="divide-y divide-ink-100 text-sm dark:divide-slate-700">
                  {(learningStats.regional_engagement.regions ?? []).map((row) => (
                    <li key={row.key} className="flex justify-between py-2 dark:text-slate-300">
                      <span>
                        {t(`admin.demo_${row.key}`, {
                          defaultValue: t(`profile.region_${row.key}`, { defaultValue: row.key }),
                        })}
                      </span>
                      <span className="font-medium">{row.count}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-ink-700/60 dark:text-slate-400">{t('admin.pollDemographicsHidden')}</p>
              )}
            </div>
            <div className="card">
              <h3 className="mb-3 font-medium text-ink-900 dark:text-slate-100">{t('admin.topTags')}</h3>
              <ul className="divide-y divide-ink-100 text-sm dark:divide-slate-700">
                {(learningStats.top_tags ?? []).map((row) => (
                  <li key={row.tag} className="flex justify-between py-2 dark:text-slate-300">
                    <span>#{row.tag}</span>
                    <span className="font-medium">{row.count}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="card">
              <h3 className="mb-3 font-medium text-ink-900 dark:text-slate-100">{t('admin.translationCompleteness')}</h3>
              <p className="mb-3 text-sm text-ink-700/60 dark:text-slate-400">
                {t('admin.translationOverall', {
                  pct: learningStats.translation?.overall_pct ?? 0,
                  done: learningStats.translation?.overall_translated ?? 0,
                  total: learningStats.translation?.overall_total ?? 0,
                })}
              </p>
              <ul className="divide-y divide-ink-100 text-sm dark:divide-slate-700">
                {(learningStats.translation?.rows ?? []).map((row) => (
                  <li key={`${row.model}-${row.field}`} className="flex justify-between gap-3 py-2 dark:text-slate-300">
                    <span>
                      {t(`admin.i18n.${row.model.replace('.', '_')}_${row.field}`, {
                        defaultValue: `${row.model} · ${row.field}`,
                      })}
                    </span>
                    <span className="shrink-0 font-medium">{row.completeness_pct}%</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>
      )}

      {activeTab === 'people' && canManagePlatformUsers && users.length > 0 && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-ink-900 dark:text-slate-100">{t('admin.userManagement')}</h2>
          <p className="mb-4 text-sm text-ink-700/60 dark:text-slate-400">
            {isAdmin ? t('admin.platformRolesHint') : t('admin.rolesHint')}
          </p>
          {isAdmin && (
            <div className="card mb-4 border-brand-100 bg-brand-50/50 dark:border-brand-900/40 dark:bg-brand-950/20">
              <h3 className="text-sm font-semibold text-ink-900 dark:text-slate-100">{t('admin.manageModerators')}</h3>
              <p className="mt-1 text-sm text-ink-700/80 dark:text-slate-400">{t('admin.manageModeratorsHint')}</p>
              {isOrgAdmin && (
                <Link to="/organization" className="mt-2 inline-block text-sm font-semibold text-brand-700 hover:underline dark:text-brand-400">
                  {t('admin.manageOrgRoles')}
                </Link>
              )}
            </div>
          )}
          {userActionError && (
            <div className="mb-4">
              <Alert>{userActionError}</Alert>
            </div>
          )}
          <div className="overflow-x-auto rounded-xl border border-ink-100 bg-white dark:border-slate-700 dark:bg-slate-800">
            <table className="min-w-full text-sm">
              <thead className="bg-ink-50 text-left text-ink-700/60 dark:bg-slate-700/50 dark:text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-medium">{t('auth.email')}</th>
                  <th className="px-4 py-3 font-medium">{t('profile.role')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.accountStatus')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.lastActivity')}</th>
                  {canManagePlatformUsers && (
                    <th className="px-4 py-3 font-medium">{t('admin.actions')}</th>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-100 dark:divide-slate-700">
                {users.map((u) => (
                  <tr key={u.id} className="dark:hover:bg-slate-700/30">
                    <td className="px-4 py-3">
                      <p className="font-medium text-ink-900 dark:text-slate-100">{u.first_name} {u.last_name}</p>
                      <p className="text-xs text-ink-700/60 dark:text-slate-400">{u.email}</p>
                    </td>
                    <td className="px-4 py-3 dark:text-slate-300">
                      {isAdmin &&
                      u.id !== currentUser?.id &&
                      (superAdmin || !['admin', 'super_admin'].includes(u.role?.name)) ? (
                        <select
                          className="input w-auto text-sm capitalize"
                          value={u.role?.name ?? 'citizen'}
                          onChange={(e) => updateUserRole(u.id, e.target.value)}
                        >
                          {ASSIGNABLE_ROLES.map((role) => (
                            <option key={role} value={role}>
                              {t(`admin.roles.${role}`)}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <span className="capitalize">{t(`admin.roles.${u.role?.name ?? 'citizen'}`)}</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {u.is_suspended ? (
                        <span className="badge bg-red-100 text-red-700">{t('admin.suspended')}</span>
                      ) : u.is_active ? (
                        <span className="badge bg-green-100 text-green-700">{t('admin.active')}</span>
                      ) : (
                        <span className="badge bg-ink-100 text-ink-700/80">{t('admin.inactive')}</span>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-ink-700/60 dark:text-slate-400">
                      {u.last_activity_at ? formatDate(u.last_activity_at) : '—'}
                    </td>
                    {canManagePlatformUsers && (
                      <td className="px-4 py-3">
                        {u.is_suspended ? (
                          <button
                            type="button"
                            className="btn-primary text-xs"
                            onClick={() => unsuspendUser(u.id)}
                          >
                            {t('admin.unsuspend')}
                          </button>
                        ) : (
                          <button
                            type="button"
                            className="btn-danger text-xs"
                            onClick={() => suspendUser(u.id)}
                          >
                            {t('admin.suspend')}
                          </button>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {activeTab === 'trust' && canManagePlatformUsers && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-ink-900 dark:text-slate-100">{t('audit.title')}</h2>
          {auditLogs.length === 0 ? (
            <div className="rounded-xl border border-dashed border-ink-200 bg-white py-8 text-center text-ink-700/60 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
              {t('audit.empty')}
            </div>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-ink-100 bg-white dark:border-slate-700 dark:bg-slate-800">
              <table className="min-w-full text-sm">
                <thead className="bg-ink-50 text-left text-ink-700/60 dark:bg-slate-700/50 dark:text-slate-400">
                  <tr>
                    <th className="px-4 py-3 font-medium">{t('audit.when')}</th>
                    <th className="px-4 py-3 font-medium">{t('audit.user')}</th>
                    <th className="px-4 py-3 font-medium">{t('audit.type')}</th>
                    <th className="px-4 py-3 font-medium">{t('audit.details')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-ink-100 dark:divide-slate-700">
                  {auditLogs.map((log) => (
                    <tr key={log.id} className="dark:hover:bg-slate-700/30">
                      <td className="px-4 py-3 whitespace-nowrap text-ink-700/60 dark:text-slate-400">
                        {formatDate(log.timestamp)}
                      </td>
                      <td className="px-4 py-3">
                        <p className="font-medium text-ink-900 dark:text-slate-100">{log.user_name || '—'}</p>
                        <p className="text-xs text-ink-700/60 dark:text-slate-400">{log.user_email}</p>
                      </td>
                      <td className="px-4 py-3 capitalize dark:text-slate-300">{log.activity_type.replace(/_/g, ' ')}</td>
                      <td className="px-4 py-3 text-xs text-ink-700/80 dark:text-slate-400">
                        {log.metadata && Object.keys(log.metadata).length > 0
                          ? JSON.stringify(log.metadata)
                          : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {activeTab === 'broadcast' && superAdmin && (
        <section>
          <div className="card">
            <h2 className="mb-2 text-lg font-semibold text-ink-900 dark:text-slate-100">{t('admin.civicSmsTitle')}</h2>
            <p className="mb-4 text-sm text-ink-700/60 dark:text-slate-400">{t('admin.civicSmsSubtitle')}</p>
            <form onSubmit={sendPlatformAlert} className="space-y-3">
              <textarea
                className="input min-h-[100px]"
                placeholder={t('admin.civicSmsPlaceholder')}
                value={platformMessage}
                onChange={(e) => setPlatformMessage(e.target.value)}
                required
                maxLength={480}
              />
              <button type="submit" className="btn-primary" disabled={!platformMessage.trim() || platformSmsBusy}>
                {platformSmsBusy ? t('common.loading') : t('admin.civicSmsSend')}
              </button>
            </form>
            <form onSubmit={sendPlatformWhatsApp} className="mt-8 space-y-3 border-t border-ink-100 pt-6 dark:border-slate-700">
              <h3 className="text-base font-semibold text-ink-900 dark:text-slate-100">{t('admin.civicWhatsAppTitle')}</h3>
              <p className="text-sm text-ink-700/60 dark:text-slate-400">{t('admin.civicWhatsAppSubtitle')}</p>
              <textarea
                className="input min-h-[100px]"
                placeholder={t('admin.civicWhatsAppPlaceholder')}
                value={platformWhatsApp}
                onChange={(e) => setPlatformWhatsApp(e.target.value)}
                required
                maxLength={1000}
              />
              <button type="submit" className="btn-primary" disabled={!platformWhatsApp.trim() || platformWhatsAppBusy}>
                {platformWhatsAppBusy ? t('common.loading') : t('admin.civicWhatsAppSend')}
              </button>
            </form>
          </div>
        </section>
      )}

      {activeTab === 'trust' && canModerate && (
      <section>
        <h2 className="mb-2 text-lg font-semibold text-ink-900 dark:text-slate-100">{t('admin.moderation')}</h2>
        <p className="mb-4 text-sm text-ink-700/60 dark:text-slate-400">{t('admin.moderationHint')}</p>
        {pendingTopics.length === 0 && pendingComments.length === 0 && forumReports.length === 0 && misinfoReports.length === 0 ? (
          <div className="rounded-xl border border-dashed border-ink-200 bg-white py-8 text-center text-ink-700/60 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
            {t('admin.nothingPending')}
          </div>
        ) : (
          <div className="space-y-3">
            {pendingTopics.map((topic) => (
              <div key={topic.id} className="card flex items-start justify-between gap-4">
                <div>
                  <span className="badge mb-1 bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">{t('admin.pendingTopics')}</span>
                  <h3 className="font-semibold text-ink-900 dark:text-slate-100">{topic.title}</h3>
                  <p className="mt-1 line-clamp-2 text-sm text-ink-700/80 dark:text-slate-400">{topic.content}</p>
                  <p className="mt-1 text-xs text-ink-700/70 dark:text-slate-500">{topic.author_name}</p>
                </div>
                <div className="flex shrink-0 gap-2">
                  <button className="btn-primary" onClick={() => moderateTopic(topic.id, true)}>
                    {t('common.approve')}
                  </button>
                  <button className="btn-danger" onClick={() => moderateTopic(topic.id, false)}>
                    {t('common.reject')}
                  </button>
                </div>
              </div>
            ))}
            {pendingComments.map((c) => (
              <div key={c.id} className="card flex items-start justify-between gap-4">
                <div>
                  <span className="badge mb-1 bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">{t('admin.pendingComments')}</span>
                  <p className="text-sm text-ink-700 dark:text-slate-300">{c.comment}</p>
                  <p className="mt-1 text-xs text-ink-700/70 dark:text-slate-500">{c.author_name}</p>
                </div>
                <div className="flex shrink-0 gap-2">
                  <button className="btn-primary" onClick={() => moderateComment(c.id, true)}>
                    {t('common.approve')}
                  </button>
                  <button className="btn-danger" onClick={() => moderateComment(c.id, false)}>
                    {t('common.reject')}
                  </button>
                </div>
              </div>
            ))}
            {forumReports.map((report) => (
              <div key={report.id} className="card flex items-start justify-between gap-4">
                <div>
                  <span className="badge mb-1 bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
                    {t('admin.forumReports')}
                  </span>
                  <p className="text-sm font-medium text-ink-900 dark:text-slate-100">
                    {t(`forum.reason_${report.reason}`)} · {report.topic_title}
                  </p>
                  {report.comment_excerpt && (
                    <p className="mt-1 text-sm text-ink-700 dark:text-slate-300">{report.comment_excerpt}</p>
                  )}
                  {report.details && (
                    <p className="mt-1 text-sm text-ink-700/80 dark:text-slate-400">{report.details}</p>
                  )}
                  <p className="mt-1 text-xs text-ink-700/70 dark:text-slate-500">{report.reporter_name}</p>
                </div>
                <div className="flex shrink-0 flex-col gap-2">
                  <button className="btn-primary" onClick={() => reviewForumReport(report.id, 'reviewed')}>
                    {t('admin.hideAndReview')}
                  </button>
                  <button className="btn-danger" onClick={() => reviewForumReport(report.id, 'dismissed')}>
                    {t('admin.dismissReport')}
                  </button>
                </div>
              </div>
            ))}
            {misinfoReports.map((report) => (
              <div key={report.id} className="card flex items-start justify-between gap-4">
                <div>
                  <span className="badge mb-1 bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
                    {t('admin.misinfoReports')}
                  </span>
                  <p className="text-sm font-medium text-ink-900 dark:text-slate-100">{report.channel}</p>
                  <p className="mt-1 text-sm text-ink-700 dark:text-slate-300">{report.description}</p>
                  {report.source_url && (
                    <p className="mt-1 break-all text-xs text-ink-700/70 dark:text-slate-500">{report.source_url}</p>
                  )}
                </div>
                <div className="flex shrink-0 flex-col gap-2">
                  <button className="btn-primary" onClick={() => reviewMisinfoReport(report.id, 'reviewed')}>
                    {t('admin.reviewReport')}
                  </button>
                  <button className="btn-danger" onClick={() => reviewMisinfoReport(report.id, 'dismissed')}>
                    {t('admin.dismissReport')}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
      )}
    </div>
  );
}

export { AdminPage };
