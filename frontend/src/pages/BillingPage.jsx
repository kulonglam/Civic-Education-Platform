import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSearchParams } from 'react-router-dom';
import { useOrganization } from '../context/OrganizationContext';
import { tenantStore } from '../lib/api';
import { Alert, PageHeader, Spinner } from '../components/ui';
import { UsageBar } from '../components/UsageBar';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { authService, billingService } from '../lib/services';

const API_ORIGIN = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api').replace(/\/api\/?$/, '');

function formatPrice(cents, currency) {
  if (cents === 0) return 'Free';
  return new Intl.NumberFormat(undefined, { style: 'currency', currency }).format(cents / 100);
}

export function BillingPage() {
  const { t } = useTranslation();
  const { isOrgAdmin } = useOrganization();
  const [params] = useSearchParams();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState('');
  const [ssoStatus, setSsoStatus] = useState({ configured: false, enabled_for_org: false });

  useEffect(() => {
    const org = tenantStore.slug;
    if (!org) return;
    authService
      .ssoStatus(org)
      .then(({ data }) => setSsoStatus(data))
      .catch(() => setSsoStatus({ configured: false, enabled_for_org: false }));
  }, []);

  const { data: plans = [], isLoading: plansLoading } = useQuery({
    queryKey: queryKeys.plans,
    queryFn: async () => {
      const { data } = await billingService.plans();
      return data.results;
    },
  });

  const { data: billing, isLoading: billingLoading, isError: billingError } = useQuery({
    queryKey: queryKeys.billing,
    queryFn: async () => {
      const { data } = await billingService.subscription();
      return data;
    },
    retry: (failureCount, error) => {
      const status = error?.response?.status;
      if (status === 503) return failureCount < 1;
      return failureCount < 2;
    },
  });

  const checkout = useMutation({
    mutationFn: (planCode) => billingService.checkout(planCode),
    onSuccess: ({ data }) => window.location.assign(data.checkout_url),
    onError: (err) => setError(extractError(err)),
    onSettled: () => setBusy(''),
  });

  const openPortal = useMutation({
    mutationFn: () => billingService.portal(),
    onSuccess: ({ data }) => window.location.assign(data.portal_url),
    onError: (err) => setError(extractError(err)),
    onSettled: () => setBusy(''),
  });

  if (plansLoading || billingLoading) return <Spinner />;

  const enterprisePlan = plans.find((plan) => plan.features?.sso);
  const hasEnterpriseSso = Boolean(billing?.subscription?.plan?.features?.sso);
  const ssoReady = ssoStatus.configured && ssoStatus.enabled_for_org;

  const statusMsg = params.get('status');

  return (
    <div>
      <PageHeader title={t('saas.billingTitle')} subtitle={t('saas.billingSubtitle')} />

      {statusMsg === 'success' && (
        <div className="mb-4">
          <Alert kind="success">{t('saas.checkoutSuccess')}</Alert>
        </div>
      )}
      {error && (
        <div className="mb-4">
          <Alert>{error}</Alert>
        </div>
      )}

      {billingError && (
        <div className="mb-4">
          <Alert>{t('saas.billingUnavailable')}</Alert>
        </div>
      )}

      {billing && (
        <div className="card mb-8">
          <h2 className="mb-4 text-lg font-semibold">{t('saas.currentPlan')}</h2>
          <p className="text-2xl font-bold text-brand-700">{billing.subscription.plan.name}</p>
          <p className="mt-1 text-sm capitalize text-gray-500">{billing.subscription.status}</p>
          <div className="mt-6 space-y-4">
            <UsageBar
              label={t('saas.members')}
              used={billing.usage.members.used}
              limit={billing.usage.members.limit}
            />
            <UsageBar
              label={t('saas.articles')}
              used={billing.usage.articles.used}
              limit={billing.usage.articles.limit}
            />
            <UsageBar
              label={t('saas.quizzes')}
              used={billing.usage.quizzes.used}
              limit={billing.usage.quizzes.limit}
            />
          </div>
          {isOrgAdmin && (
            <button
              type="button"
              className="btn-secondary mt-6"
              onClick={() => {
                setBusy('portal');
                openPortal.mutate();
              }}
              disabled={!!busy}
            >
              {t('saas.manageBilling')}
            </button>
          )}
        </div>
      )}

      <h2 className="mb-4 text-lg font-semibold">{t('saas.availablePlans')}</h2>
      <div className="grid gap-4 md:grid-cols-3">
        {plans.map((plan, idx) => {
          const isCurrent = billing?.subscription.plan.code === plan.code;
          const isPopular = idx === 1 && plans.length >= 2;
          return (
            <div
              key={plan.id}
              className={`card relative flex flex-col transition-shadow ${
                isCurrent
                  ? 'ring-2 ring-brand-500 dark:ring-brand-400'
                  : isPopular
                    ? 'shadow-lg ring-1 ring-brand-200 dark:ring-brand-700'
                    : ''
              }`}
            >
              {isPopular && !isCurrent && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-brand-600 px-3 py-0.5 text-xs font-semibold text-white shadow">
                  {t('saas.mostPopular')}
                </span>
              )}
              {isCurrent && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-emerald-600 px-3 py-0.5 text-xs font-semibold text-white shadow">
                  {t('saas.currentPlanBadge')}
                </span>
              )}
              <h3 className="text-xl font-bold dark:text-slate-100">{plan.name}</h3>
              <p className="mt-2 text-3xl font-semibold dark:text-slate-100">
                {formatPrice(plan.price_cents, plan.currency)}
                {plan.price_cents > 0 && (
                  <span className="text-sm font-normal text-gray-500 dark:text-slate-400">/{plan.interval}</span>
                )}
              </p>
              <ul className="mt-4 flex-1 space-y-2 text-sm text-gray-600 dark:text-slate-400">
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-brand-500" />
                  {plan.max_members ?? '∞'} {t('saas.members')}
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-brand-500" />
                  {plan.max_articles ?? '∞'} {t('saas.articles')}
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-brand-500" />
                  {plan.max_quizzes ?? '∞'} {t('saas.quizzes')}
                </li>
              </ul>
              {isOrgAdmin && !isCurrent && (
                <button
                  type="button"
                  className={`mt-6 w-full ${isPopular ? 'btn-primary' : 'btn-secondary'}`}
                  disabled={busy === plan.code || checkout.isPending}
                  onClick={() => {
                    setError('');
                    setBusy(plan.code);
                    checkout.mutate(plan.code);
                  }}
                >
                  {busy === plan.code ? t('common.loading') : t('saas.upgrade')}
                </button>
              )}
              {isCurrent && (
                <div className="mt-6 rounded-lg bg-emerald-50 py-2 text-center text-sm font-medium text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400">
                  ✓ {t('saas.currentPlanBadge')}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="card mt-8 border-brand-100 bg-brand-50">
        <h2 className="text-lg font-semibold text-brand-900">{t('billing.enterpriseTitle')}</h2>
        {hasEnterpriseSso ? (
          <>
            <p className="mt-2 text-sm text-gray-600">
              {ssoReady ? t('billing.enterpriseSsoReady') : t('billing.enterpriseSsoSetup')}
            </p>
            {ssoReady && (
              <button
                type="button"
                className="btn-primary mt-4 text-sm"
                onClick={() => {
                  const org = tenantStore.slug;
                  if (org) {
                    window.location.assign(
                      `${API_ORIGIN}/api/auth/sso/login/?org=${encodeURIComponent(org)}`
                    );
                  }
                }}
              >
                {t('auth.ssoLogin')}
              </button>
            )}
          </>
        ) : (
          <>
            <p className="mt-2 text-sm text-gray-600">{t('billing.enterpriseSsoHint')}</p>
            {enterprisePlan && (
              <p className="mt-2 text-xs text-gray-500">
                {t('billing.enterpriseUpgradeHint', { plan: enterprisePlan.name })}
              </p>
            )}
            <a href="mailto:support@civiceducation.ss" className="btn-secondary mt-4 inline-block text-sm">
              {t('billing.contactSupport')}
            </a>
          </>
        )}
      </div>
    </div>
  );
}
