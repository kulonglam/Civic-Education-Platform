import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import toast from 'react-hot-toast';
import { analyticsService, auditService, forumService, notificationService, notifyService, organizationService, securityService, userService } from '../lib/services';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import { extractError } from '../lib/api';
import { Alert, PageHeader, Spinner } from '../components/ui';
import { formatDate } from '../lib/format';

function StatCard({ label, value }) {
  return (
    <div className="card dark:border-slate-700 dark:bg-slate-800">
      <p className="text-sm text-gray-500 dark:text-slate-400">{label}</p>
      <p className="mt-1 text-3xl font-bold text-gray-900 dark:text-slate-100">{value}</p>
    </div>
  );
}

function AdminPage() {
  const { t } = useTranslation();
  const { user: currentUser, hasRole, isPlatformAdmin } = useAuth();
  const { isOrgModerator } = useOrganization();
  const isAdmin = isPlatformAdmin();
  const canModerateUsers = hasRole('admin', 'moderator') || isOrgModerator;
  const canManagePlatformUsers = hasRole('admin', 'moderator');
  const ASSIGNABLE_ROLES = ['citizen', 'editor', 'moderator', 'admin'];
  const [overview, setOverview] = useState(null);
  const [quizStats, setQuizStats] = useState([]);
  const [forumStats, setForumStats] = useState(null);
  const [learningStats, setLearningStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [userActionError, setUserActionError] = useState('');
  const [pendingTopics, setPendingTopics] = useState([]);
  const [pendingComments, setPendingComments] = useState([]);
  const [platformMessage, setPlatformMessage] = useState('');
  const [platformSmsBusy, setPlatformSmsBusy] = useState(false);
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
  const [supportBusy, setSupportBusy] = useState(false);
  const [sloMetrics, setSloMetrics] = useState(null);
  const [platformCases, setPlatformCases] = useState([]);

  const loadModeration = () =>
    forumService
      .pending()
      .then((r) => {
        setPendingTopics(r.data.topics);
        setPendingComments(r.data.comments);
      })
      .catch(() => {});

  useEffect(() => {
    const tasks = [loadModeration()];
    if (isAdmin) {
      tasks.push(
        analyticsService.overview().then((r) => setOverview(r.data)),
        analyticsService.quizzes().then((r) => setQuizStats(r.data)),
        analyticsService.forum().then((r) => setForumStats(r.data)),
        analyticsService.learning().then((r) => setLearningStats(r.data)),
        notificationService.pushStats().then((r) => setPushStats(r.data)),
        organizationService.platformOrgs().then((r) => setPlatformOrgs(r.data.results ?? r.data)),
        organizationService.platformUsage().then((r) => setUsageSummary(r.data)),
        securityService.events({ page_size: 40 }).then((r) => setSecurityEvents(r.data.results ?? [])),
        organizationService.platformSlo().then((r) => setSloMetrics(r.data)),
        organizationService.platformSupportCases().then((r) => setPlatformCases(r.data.results ?? r.data)),
      );
    }
    if (canManagePlatformUsers) {
      tasks.push(userService.list().then((r) => setUsers(r.data.results ?? r.data)));
      tasks.push(
        auditService.logs({ page_size: 50 }).then((r) => setAuditLogs(r.data.results ?? r.data)),
      );
    }
    Promise.allSettled(tasks).finally(() => setLoading(false));
  }, [isAdmin, canModerateUsers, canManagePlatformUsers]);

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

  const moderateTopic = async (id, approve) => {
    await forumService.moderateTopic(id, approve);
    loadModeration();
  };

  const moderateComment = async (id, approve) => {
    await forumService.moderateComment(id, approve);
    loadModeration();
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

  if (loading) return <Spinner />;

  return (
    <div className="space-y-10">
      <PageHeader
        title={isAdmin ? t('admin.platformTitle') : t('admin.moderationTitle')}
        subtitle={isAdmin ? t('admin.platformSubtitle') : t('admin.moderationSubtitle')}
      />

      <div className="card border-brand-100 bg-brand-50/60 dark:border-brand-900/40 dark:bg-brand-950/30">
        <h2 className="text-sm font-semibold text-brand-900 dark:text-brand-200">{t('roles.modelTitle')}</h2>
        <ul className="mt-2 space-y-1 text-sm text-gray-700 dark:text-slate-300">
          <li><strong>{t('roles.platformRole')}:</strong> {t('roles.platformRoleDesc')}</li>
          <li><strong>{t('roles.orgRole')}:</strong> {t('roles.orgRoleDesc')}</li>
        </ul>
        {!isAdmin && (
          <p className="mt-3 text-sm text-gray-600 dark:text-slate-400">{t('admin.moderationPanelDesc')}</p>
        )}
      </div>

      {isAdmin && overview && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('admin.overview')}</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label={t('admin.totalUsers')} value={overview.total_users} />
            <StatCard label={t('admin.activeUsers')} value={overview.active_users_30d} />
            <StatCard label={t('admin.articlesPublished')} value={overview.articles_published} />
            <StatCard label={t('admin.quizCompletions')} value={overview.quiz_completions} />
          </div>
        </section>
      )}

      {isAdmin && (
        <section>
          <h2 className="mb-2 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('admin.platformOrgs')}</h2>
          <p className="mb-4 text-sm text-gray-500 dark:text-slate-400">{t('admin.platformOrgsSubtitle')}</p>
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
          <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-slate-700 dark:bg-slate-800">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-left text-gray-500 dark:bg-slate-700/50 dark:text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-medium">{t('saas.orgName')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.plan')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.membersCount')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.accountStatus')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.actions')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-slate-700">
                {platformOrgs.map((org) => (
                  <tr key={org.id} className="dark:hover:bg-slate-700/30">
                    <td className="px-4 py-3">
                      <p className="font-medium text-gray-900 dark:text-slate-100">{org.name}</p>
                      <p className="text-xs text-gray-500 dark:text-slate-400">{org.slug}</p>
                    </td>
                    <td className="px-4 py-3 dark:text-slate-300">{org.plan_code || '—'}</td>
                    <td className="px-4 py-3 dark:text-slate-300">{org.member_count ?? '—'}</td>
                    <td className="px-4 py-3">
                      {org.is_active ? (
                        <span className="badge bg-green-100 text-green-700">{t('admin.active')}</span>
                      ) : (
                        <span className="badge bg-gray-100 text-gray-600">{t('admin.inactive')}</span>
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
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {isAdmin && supportOrg && (
        <section className="card">
          <div className="mb-3 flex items-center justify-between gap-2">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
              {t('admin.supportView')}: {supportOrg.name}
            </h2>
            <button type="button" className="btn-secondary text-xs" onClick={() => setSupportOrg(null)}>
              {t('common.close')}
            </button>
          </div>
          <p className="mb-4 text-sm text-gray-500 dark:text-slate-400">{t('admin.supportViewHint')}</p>
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
        </section>
      )}

      {isAdmin && usageSummary?.totals && (
        <section>
          <h2 className="mb-2 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('admin.usageSummary')}</h2>
          <p className="mb-4 text-sm text-gray-500 dark:text-slate-400">{t('admin.usageSummarySubtitle')}</p>
          <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label={t('admin.platformOrgs')} value={usageSummary.totals.organizations} />
            <StatCard label={t('admin.membersCount')} value={usageSummary.totals.members} />
            <StatCard label={t('dashboard.quizAttempts')} value={usageSummary.totals.quiz_attempts} />
            <StatCard label={t('admin.activeLearners')} value={usageSummary.totals.active_learners_30d} />
          </div>
        </section>
      )}

      {isAdmin && sloMetrics && (
        <section>
          <h2 className="mb-2 text-lg font-semibold text-gray-900 dark:text-slate-100">SLO status</h2>
          <p className="mb-4 text-sm text-gray-500 dark:text-slate-400">
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
            <ul className="mb-6 divide-y divide-gray-100 rounded-xl border border-gray-200 bg-white text-sm dark:divide-slate-700 dark:border-slate-700 dark:bg-slate-800">
              {platformCases.slice(0, 8).map((c) => (
                <li key={c.id} className="flex flex-wrap items-center justify-between gap-2 px-4 py-3">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-slate-100">{c.subject}</p>
                    <p className="text-xs text-gray-500 dark:text-slate-400">
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

      {isAdmin && securityEvents.length > 0 && (
        <section>
          <h2 className="mb-2 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('admin.securityEvents')}</h2>
          <p className="mb-4 text-sm text-gray-500 dark:text-slate-400">{t('admin.securityEventsSubtitle')}</p>
          <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-slate-700 dark:bg-slate-800">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-left text-gray-500 dark:bg-slate-700/50 dark:text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-medium">{t('audit.when')}</th>
                  <th className="px-4 py-3 font-medium">{t('audit.type')}</th>
                  <th className="px-4 py-3 font-medium">{t('audit.user')}</th>
                  <th className="px-4 py-3 font-medium">IP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-slate-700">
                {securityEvents.map((ev) => (
                  <tr key={ev.id} className="dark:hover:bg-slate-700/30">
                    <td className="px-4 py-3 whitespace-nowrap text-gray-500 dark:text-slate-400">
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

      {isAdmin && pushStats && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('admin.pushTitle')}</h2>
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

      {isAdmin && forumStats && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('admin.forumEngagement')}</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label={t('admin.totalTopics')} value={forumStats.total_topics} />
            <StatCard label={t('admin.totalComments')} value={forumStats.total_comments} />
            <StatCard label={t('admin.pendingTopics')} value={forumStats.pending_topics} />
            <StatCard label={t('admin.pendingComments')} value={forumStats.pending_comments} />
          </div>
        </section>
      )}

      {isAdmin && quizStats.length > 0 && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('admin.quizPerformance')}</h2>
          <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-slate-700 dark:bg-slate-800">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-left text-gray-500 dark:bg-slate-700/50 dark:text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-medium">{t('quizzes.title')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.attempts')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.passRate')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.avgScore')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-slate-700">
                {quizStats.map((q) => (
                  <tr key={q.quiz_id} className="dark:hover:bg-slate-700/30">
                    <td className="px-4 py-3 font-medium text-gray-900 dark:text-slate-100">{q.title}</td>
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

      {isAdmin && learningStats && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('admin.learningInsights')}</h2>
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="card">
              <h3 className="mb-3 font-medium text-gray-900 dark:text-slate-100">{t('admin.articlesByCategory')}</h3>
              <ul className="divide-y divide-gray-100 text-sm dark:divide-slate-700">
                {(learningStats.articles_by_category ?? []).map((row) => (
                  <li key={row.slug} className="flex justify-between py-2 dark:text-slate-300">
                    <span>{row.category}</span>
                    <span className="font-medium">{row.article_count}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="card">
              <h3 className="mb-3 font-medium text-gray-900 dark:text-slate-100">{t('admin.topTags')}</h3>
              <ul className="divide-y divide-gray-100 text-sm dark:divide-slate-700">
                {(learningStats.top_tags ?? []).map((row) => (
                  <li key={row.tag} className="flex justify-between py-2 dark:text-slate-300">
                    <span>#{row.tag}</span>
                    <span className="font-medium">{row.count}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>
      )}

      {canManagePlatformUsers && users.length > 0 && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('admin.userManagement')}</h2>
          {isAdmin && (
            <p className="mb-4 text-sm text-gray-500 dark:text-slate-400">
              {isAdmin ? t('admin.platformRolesHint') : t('admin.rolesHint')}
            </p>
          )}
          {userActionError && (
            <div className="mb-4">
              <Alert>{userActionError}</Alert>
            </div>
          )}
          <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-slate-700 dark:bg-slate-800">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-left text-gray-500 dark:bg-slate-700/50 dark:text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-medium">{t('auth.email')}</th>
                  <th className="px-4 py-3 font-medium">{t('profile.role')}</th>
                  <th className="px-4 py-3 font-medium">{t('admin.accountStatus')}</th>
                  {canManagePlatformUsers && (
                    <th className="px-4 py-3 font-medium">{t('admin.actions')}</th>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-slate-700">
                {users.map((u) => (
                  <tr key={u.id} className="dark:hover:bg-slate-700/30">
                    <td className="px-4 py-3">
                      <p className="font-medium text-gray-900 dark:text-slate-100">{u.first_name} {u.last_name}</p>
                      <p className="text-xs text-gray-500 dark:text-slate-400">{u.email}</p>
                    </td>
                    <td className="px-4 py-3 dark:text-slate-300">
                      {isAdmin && u.id !== currentUser?.id ? (
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
                        <span className="badge bg-gray-100 text-gray-600">{t('admin.inactive')}</span>
                      )}
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

      {canManagePlatformUsers && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('audit.title')}</h2>
          {auditLogs.length === 0 ? (
            <div className="rounded-xl border border-dashed border-gray-300 bg-white py-8 text-center text-gray-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
              {t('audit.empty')}
            </div>
          ) : (
            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-slate-700 dark:bg-slate-800">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-left text-gray-500 dark:bg-slate-700/50 dark:text-slate-400">
                  <tr>
                    <th className="px-4 py-3 font-medium">{t('audit.when')}</th>
                    <th className="px-4 py-3 font-medium">{t('audit.user')}</th>
                    <th className="px-4 py-3 font-medium">{t('audit.type')}</th>
                    <th className="px-4 py-3 font-medium">{t('audit.details')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-slate-700">
                  {auditLogs.map((log) => (
                    <tr key={log.id} className="dark:hover:bg-slate-700/30">
                      <td className="px-4 py-3 whitespace-nowrap text-gray-500 dark:text-slate-400">
                        {formatDate(log.timestamp)}
                      </td>
                      <td className="px-4 py-3">
                        <p className="font-medium text-gray-900 dark:text-slate-100">{log.user_name || '—'}</p>
                        <p className="text-xs text-gray-500 dark:text-slate-400">{log.user_email}</p>
                      </td>
                      <td className="px-4 py-3 capitalize dark:text-slate-300">{log.activity_type.replace(/_/g, ' ')}</td>
                      <td className="px-4 py-3 text-xs text-gray-600 dark:text-slate-400">
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

      {isAdmin && (
        <section>
          <div className="card">
            <h2 className="mb-2 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('admin.civicSmsTitle')}</h2>
            <p className="mb-4 text-sm text-gray-500 dark:text-slate-400">{t('admin.civicSmsSubtitle')}</p>
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
          </div>
        </section>
      )}

      <section>
        <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('admin.moderation')}</h2>
        {pendingTopics.length === 0 && pendingComments.length === 0 ? (
          <div className="rounded-xl border border-dashed border-gray-300 bg-white py-8 text-center text-gray-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
            {t('admin.nothingPending')}
          </div>
        ) : (
          <div className="space-y-3">
            {pendingTopics.map((topic) => (
              <div key={topic.id} className="card flex items-start justify-between gap-4">
                <div>
                  <span className="badge mb-1 bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">{t('admin.pendingTopics')}</span>
                  <h3 className="font-semibold text-gray-900 dark:text-slate-100">{topic.title}</h3>
                  <p className="mt-1 line-clamp-2 text-sm text-gray-600 dark:text-slate-400">{topic.content}</p>
                  <p className="mt-1 text-xs text-gray-400 dark:text-slate-500">{topic.author_name}</p>
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
                  <p className="text-sm text-gray-700 dark:text-slate-300">{c.comment}</p>
                  <p className="mt-1 text-xs text-gray-400 dark:text-slate-500">{c.author_name}</p>
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
          </div>
        )}
      </section>
    </div>
  );
}

export { AdminPage };
