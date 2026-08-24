import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Alert, EmptyState, PageHeader, Spinner } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { engagementService } from '../lib/services';

function PollCard({ poll, onVote, votingId }) {
  const { t } = useTranslation();
  const total = poll.total_votes || 0;
  const showResults = Boolean(poll.results_visible);

  return (
    <article className="surface p-5">
      <div className="mb-2 flex flex-wrap gap-2">
        <span className="badge bg-brand-50 text-brand-800 dark:bg-brand-900/30 dark:text-brand-200">
          {t(`engage.kind_${poll.kind || 'community'}`)}
        </span>
        <span className="text-xs text-ink-700/60 dark:text-slate-400">
          {t('engage.totalResponses', { count: total })}
        </span>
      </div>
      <h3 className="font-display text-lg font-semibold text-ink-900 dark:text-slate-100">{poll.question}</h3>
      {poll.description && (
        <p className="mt-2 text-sm text-ink-700/70 dark:text-slate-400">{poll.description}</p>
      )}
      <ul className="mt-4 space-y-2">
        {poll.options.map((opt) => {
          const pct = showResults && total > 0 ? Math.round((opt.vote_count / total) * 100) : 0;
          const selected = poll.user_vote_option_id === opt.id;
          return (
            <li key={opt.id}>
              <button
                type="button"
                className={`w-full rounded-lg border px-3 py-2 text-left text-sm transition-colors ${
                  selected
                    ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/30'
                    : 'border-ink-100 hover:border-brand-200 dark:border-slate-700'
                }`}
                disabled={!poll.is_open || Boolean(poll.user_vote_option_id) || votingId === poll.id}
                onClick={() => onVote(poll.id, opt.id)}
              >
                <span className="flex items-center justify-between gap-2">
                  <span>{opt.label}</span>
                  <span className="text-xs text-ink-700/60 dark:text-slate-400">
                    {showResults ? `${pct}%` : ''}
                  </span>
                </span>
                {showResults && (
                  <div className="mt-1.5 h-1 overflow-hidden rounded-full bg-ink-100 dark:bg-slate-700">
                    <div className="h-full bg-brand-600" style={{ width: `${pct}%` }} />
                  </div>
                )}
              </button>
            </li>
          );
        })}
      </ul>
      {!poll.is_open && (
        <p className="mt-3 text-xs text-ink-700/55 dark:text-slate-400">{t('engage.pollClosed')}</p>
      )}
    </article>
  );
}

function PetitionCard({ petition, onSign, signingId }) {
  const { t } = useTranslation();
  const pct = Math.min(100, Math.round((petition.signature_count / petition.goal_signatures) * 100));

  return (
    <article className="surface p-5">
      <h3 className="font-display text-lg font-semibold text-ink-900 dark:text-slate-100">{petition.title}</h3>
      <p className="mt-2 text-sm text-ink-700/70 dark:text-slate-400">{petition.description}</p>
      <div className="mt-4">
        <div className="mb-1 flex justify-between text-xs text-ink-700/60 dark:text-slate-400">
          <span>
            {petition.signature_count} / {petition.goal_signatures} {t('engage.signatures')}
          </span>
          <span>{pct}%</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-ink-100 dark:bg-slate-700">
          <div className="h-full rounded-full bg-brand-600" style={{ width: `${pct}%` }} />
        </div>
      </div>
      <button
        type="button"
        className="btn-primary mt-4 text-sm"
        disabled={petition.user_signed || petition.status !== 'open' || signingId === petition.id}
        onClick={() => onSign(petition.id)}
      >
        {petition.user_signed ? t('engage.signed') : t('engage.signPetition')}
      </button>
    </article>
  );
}

function CampaignCard({ campaign, onJoin, joiningId }) {
  const { t } = useTranslation();

  return (
    <article className="surface p-5">
      <h3 className="font-display text-lg font-semibold text-ink-900 dark:text-slate-100">{campaign.title}</h3>
      <p className="mt-2 text-sm text-ink-700/70 dark:text-slate-400">{campaign.description}</p>
      <p className="mt-2 text-xs text-ink-700/55 dark:text-slate-400">
        {t('engage.joinedCount', { count: campaign.signup_count || 0 })}
      </p>
      <div className="mt-4 flex flex-wrap items-center gap-3">
        <button
          type="button"
          className="btn-primary text-sm"
          disabled={campaign.user_joined || campaign.status !== 'active' || joiningId === campaign.id}
          onClick={() => onJoin(campaign.id)}
        >
          {campaign.user_joined ? t('engage.joined') : t('engage.joinCampaign')}
        </button>
        {campaign.link_url && (
          <a
            href={campaign.link_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-semibold text-brand-700 hover:underline dark:text-brand-300"
          >
            {t('engage.learnMore')} →
          </a>
        )}
      </div>
    </article>
  );
}

export function EngagementPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { hasRole } = useAuth();
  const { isOrgContentManager } = useOrganization();
  const canManage = hasRole('admin', 'editor') || isOrgContentManager;
  const [kind, setKind] = useState('');

  const { data: polls = [], isLoading: pollsLoading, error: pollsError } = useQuery({
    queryKey: queryKeys.engagementPolls(kind),
    queryFn: async () => {
      const params = kind ? { kind } : undefined;
      const { data } = await engagementService.polls(params);
      return data;
    },
  });

  const { data: petitions = [], isLoading: petitionsLoading, error: petitionsError } = useQuery({
    queryKey: queryKeys.engagementPetitions,
    queryFn: async () => {
      const { data } = await engagementService.petitions();
      return data;
    },
  });

  const { data: campaigns = [], isLoading: campaignsLoading, error: campaignsError } = useQuery({
    queryKey: queryKeys.engagementCampaigns,
    queryFn: async () => {
      const { data } = await engagementService.campaigns();
      return data;
    },
  });

  const vote = useMutation({
    mutationFn: ({ pollId, optionId }) => engagementService.votePoll(pollId, optionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['engagement', 'polls'] });
      queryClient.invalidateQueries({ queryKey: queryKeys.gamificationMe });
    },
  });

  const sign = useMutation({
    mutationFn: (petitionId) => engagementService.signPetition(petitionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.engagementPetitions });
      queryClient.invalidateQueries({ queryKey: queryKeys.gamificationMe });
    },
  });

  const join = useMutation({
    mutationFn: (campaignId) => engagementService.joinCampaign(campaignId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.engagementCampaigns });
      queryClient.invalidateQueries({ queryKey: queryKeys.gamificationMe });
    },
  });

  const loading = pollsLoading || petitionsLoading || campaignsLoading;
  const error = pollsError || petitionsError || campaignsError;

  if (loading) return <Spinner />;

  return (
    <div className="mx-auto max-w-4xl">
      <PageHeader title={t('engage.title')} subtitle={t('engage.subtitle')} />
      {canManage && (
        <div className="mb-6 flex justify-end">
          <Link to="/engage/manage" className="btn-secondary text-sm">
            {t('engage.manageLink')}
          </Link>
        </div>
      )}
      <p className="mb-8 text-sm leading-relaxed text-ink-700/80 dark:text-slate-300">
        {t('engage.pollsIntro')}
      </p>

      {error && (
        <div className="mb-6">
          <Alert>{extractError(error)}</Alert>
        </div>
      )}

      {(vote.error || sign.error || join.error) && (
        <div className="mb-6">
          <Alert>{extractError(vote.error || sign.error || join.error)}</Alert>
        </div>
      )}

      <section className="mb-10">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h2 className="font-display text-xl font-semibold text-ink-900 dark:text-slate-100">
            {t('engage.polls')}
          </h2>
          <select
            className="input w-auto"
            value={kind}
            onChange={(e) => setKind(e.target.value)}
            aria-label={t('engage.pollKind')}
          >
            <option value="">{t('engage.allPolls')}</option>
            <option value="educational">{t('engage.kind_educational')}</option>
            <option value="community">{t('engage.kind_community')}</option>
          </select>
        </div>
        {polls.length === 0 ? (
          <EmptyState title={t('engage.noPolls')} />
        ) : (
          <div className="space-y-4">
            {polls.map((poll) => (
              <PollCard
                key={poll.id}
                poll={poll}
                votingId={vote.variables?.pollId}
                onVote={(pollId, optionId) => vote.mutate({ pollId, optionId })}
              />
            ))}
          </div>
        )}
      </section>

      <section className="mb-10">
        <h2 className="mb-4 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">
          {t('engage.petitions')}
        </h2>
        {petitions.length === 0 ? (
          <EmptyState title={t('engage.noPetitions')} />
        ) : (
          <div className="space-y-4">
            {petitions.map((petition) => (
              <PetitionCard
                key={petition.id}
                petition={petition}
                signingId={sign.variables}
                onSign={(id) => sign.mutate(id)}
              />
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-4 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">
          {t('engage.campaigns')}
        </h2>
        {campaigns.length === 0 ? (
          <EmptyState title={t('engage.noCampaigns')} />
        ) : (
          <div className="space-y-4">
            {campaigns.map((campaign) => (
              <CampaignCard
                key={campaign.id}
                campaign={campaign}
                joiningId={join.variables}
                onJoin={(id) => join.mutate(id)}
              />
            ))}
          </div>
        )}
      </section>

      <p className="mt-8 text-center text-sm text-ink-700/60 dark:text-slate-400">
        <Link to="/dashboard" className="font-semibold text-brand-700 hover:underline dark:text-brand-300">
          {t('engage.viewProgress')}
        </Link>
      </p>
    </div>
  );
}
