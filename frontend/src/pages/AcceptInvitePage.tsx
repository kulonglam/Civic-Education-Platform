import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { organizationService } from '../lib/services';
import { extractError } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { tenantStore } from '../lib/api';
import { Alert, PageHeader, Spinner } from '../components/ui';

function AcceptInvitePage() {
  const { token } = useParams();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [invite, setInvite] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    (async () => {
      try {
        const { data } = await organizationService.invitePreview(token);
        setInvite(data);
      } catch (err) {
        setError(extractError(err));
      } finally {
        setLoading(false);
      }
    })();
  }, [token]);

  const accept = async () => {
    if (!token) return;
    setAccepting(true);
    setError('');
    try {
      await organizationService.acceptInvite(token);
      if (invite?.organization?.slug) {
        tenantStore.set(invite.organization.slug);
      }
      navigate('/organization', { replace: true });
    } catch (err) {
      setError(extractError(err));
    } finally {
      setAccepting(false);
    }
  };

  if (loading) return <Spinner className="min-h-[45vh]" />;

  if (!invite) {
    return (
      <div className="mx-auto max-w-md card">
        <Alert>{error || t('saas.inviteInvalid')}</Alert>
        <Link to="/" className="btn-primary mt-4 inline-block">{t('nav.home')}</Link>
      </div>
    );
  }

  if (invite.is_expired) {
    return (
      <div className="mx-auto max-w-md card">
        <Alert>{t('saas.inviteExpired')}</Alert>
      </div>
    );
  }

  const emailMatches = Boolean(user?.email?.toLowerCase() === invite.email.toLowerCase());
  const registerUrl = `/register?invite=${encodeURIComponent(token ?? '')}&email=${encodeURIComponent(invite.email ?? '')}`;
  const loginUrl = `/login?next=${encodeURIComponent(`/invite/${token ?? ''}`)}`;

  return (
    <div className="mx-auto max-w-lg">
      <PageHeader
        title={t('saas.inviteTitle')}
        subtitle={t('saas.inviteSubtitle', { org: invite.organization.name ?? '' })}
      />
      {error && (
        <div className="mb-4">
          <Alert>{error}</Alert>
        </div>
      )}
      <div className="card space-y-4">
        <p className="text-ink-700/80 dark:text-slate-300">
          {t('saas.inviteRole', { role: invite.role, email: invite.email })}
        </p>
        {user ? (
          emailMatches ? (
            <button type="button" className="btn-primary" onClick={accept} disabled={accepting}>
              {accepting ? t('common.loading') : t('saas.acceptInvite')}
            </button>
          ) : (
            <Alert>
              {t('saas.inviteWrongAccount', { email: invite.email })}
            </Alert>
          )
        ) : (
          <div className="flex flex-col gap-2 sm:flex-row">
            <Link to={registerUrl} className="btn-primary text-center">{t('saas.registerToAccept')}</Link>
            <Link to={loginUrl} className="btn-secondary text-center">{t('nav.login')}</Link>
          </div>
        )}
      </div>
    </div>
  );
}

export { AcceptInvitePage };
