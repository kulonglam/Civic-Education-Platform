import { useState, type FormEvent } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Alert, PageHeader, Spinner } from '../components/ui';
import { GuestSaveCta } from '../components/GuestSaveCta';
import { AcademicCap, Eye, FileText, Megaphone, ShieldCheck, Target } from '../components/Icons';
import { useAuth } from '../context/AuthContext';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { awarenessService } from '../lib/services';
import { PAGE_COVERS } from '../lib/civicPhotos';
import type { AwarenessReportPayload } from '../types/api';

const REPORT_CHANNELS = ['whatsapp', 'facebook', 'website', 'radio', 'other'];

const CARD_ICONS = {
  quiz: AcademicCap,
  verify: Eye,
  examples: FileText,
  social: Megaphone,
  credibility: ShieldCheck,
  report: Target,
};

export function AwarenessPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    channel: 'whatsapp',
    description: '',
    source_url: '',
    reporter_contact: '',
  });
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState(false);

  const { data, isLoading, isError } = useQuery({
    queryKey: queryKeys.awareness(),
    queryFn: async () => {
      const { data: res } = await awarenessService.overview();
      return res;
    },
  });

  const reportMutation = useMutation({
    mutationFn: (payload: AwarenessReportPayload) => awarenessService.report(payload),
    onSuccess: () => {
      setFormSuccess(true);
      setFormError('');
      setForm({
        channel: 'whatsapp',
        description: '',
        source_url: '',
        reporter_contact: '',
      });
      queryClient.invalidateQueries({ queryKey: queryKeys.awarenessReports });
    },
    onError: (err) => {
      setFormSuccess(false);
      setFormError(extractError(err));
    },
  });

  const lessonsByKey = Object.fromEntries((data?.lessons ?? []).map((item) => [item.key, item]));
  const quiz = data?.quiz;

  const cards = [
    { key: 'quiz', to: quiz?.id ? `/quizzes/${quiz.id}` : '/quizzes' },
    { key: 'verify', to: lessonsByKey.verify?.article_id ? `/articles/${lessonsByKey.verify.article_id}` : '/articles?category=media-misinformation' },
    { key: 'examples', to: lessonsByKey.examples?.article_id ? `/articles/${lessonsByKey.examples.article_id}` : '/articles?category=media-misinformation' },
    { key: 'social', to: lessonsByKey.social?.article_id ? `/articles/${lessonsByKey.social.article_id}` : '/articles?category=media-misinformation' },
    { key: 'credibility', to: lessonsByKey.credibility?.article_id ? `/articles/${lessonsByKey.credibility.article_id}` : '/articles?category=media-misinformation' },
    { key: 'report', href: '#report' },
  ];

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setFormSuccess(false);
    reportMutation.mutate({
      channel: form.channel,
      description: form.description.trim(),
      source_url: form.source_url.trim(),
      reporter_contact: form.reporter_contact.trim(),
    });
  };

  return (
    <div className="page-shell">
      <PageHeader
        eyebrow={t('nav.learn')}
        title={t('awareness.title')}
        subtitle={t('awareness.subtitle')}
        coverSrc={PAGE_COVERS.awareness}
        coverAlt={t('photos.communityWork')}
      />

      {isError && <Alert>{t('common.noResults')}</Alert>}
      {isLoading && <Spinner />}

      <div className="mt-2 grid gap-4 sm:grid-cols-2">
        {cards.map((card) => {
          const Icon = CARD_ICONS[card.key as keyof typeof CARD_ICONS];
          const inner = (
            <>
              <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-100 text-brand-700 dark:bg-brand-900/50 dark:text-brand-300">
                <Icon className="h-5 w-5" />
              </div>
              <h2 className="font-display text-lg font-semibold text-ink-900 dark:text-slate-100">
                {t(`awareness.cards.${card.key}.title`)}
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-ink-700/75 dark:text-slate-400">
                {t(`awareness.cards.${card.key}.text`)}
              </p>
            </>
          );
          const className = 'card block p-5 transition hover:-translate-y-0.5 hover:shadow-lift';
          if (card.href) {
            return (
              <a key={card.key} href={card.href} className={className}>
                {inner}
              </a>
            );
          }
          return (
            <Link key={card.key} to={card.to ?? '/'} className={className}>
              {inner}
            </Link>
          );
        })}
      </div>

      {quiz && !user && (
        <GuestSaveCta className="mt-8" />
      )}

      <section id="report" className="mt-12 scroll-mt-24">
        <h2 className="font-display text-2xl font-semibold text-ink-900 dark:text-slate-100">
          {t('awareness.reportTitle')}
        </h2>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-ink-700/75 dark:text-slate-400">
          {t('awareness.reportIntro')}
        </p>
        {formSuccess && (
          <div className="mt-4">
            <Alert kind="success">{t('awareness.reportThanks')}</Alert>
          </div>
        )}
        {formError && (
          <div className="mt-4">
            <Alert>{formError}</Alert>
          </div>
        )}
        <form className="mt-6 grid max-w-2xl gap-4" onSubmit={handleSubmit}>
          <label className="grid gap-1 text-sm font-medium">
            {t('awareness.fields.channel')}
            <select
              className="input"
              value={form.channel}
              onChange={(e) => setForm((prev) => ({ ...prev, channel: e.target.value }))}
            >
              {REPORT_CHANNELS.map((value) => (
                <option key={value} value={value}>
                  {t(`awareness.channels.${value}`)}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-1 text-sm font-medium">
            {t('awareness.fields.description')}
            <textarea
              className="input min-h-[8rem]"
              required
              minLength={40}
              maxLength={2000}
              value={form.description}
              onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
            />
            <span className="font-normal text-xs text-ink-700/55 dark:text-slate-500">
              {t('awareness.fields.descriptionHint')}
            </span>
          </label>
          <label className="grid gap-1 text-sm font-medium">
            {t('awareness.fields.sourceUrl')}
            <input
              className="input"
              value={form.source_url}
              onChange={(e) => setForm((prev) => ({ ...prev, source_url: e.target.value }))}
            />
          </label>
          {!user && (
            <label className="grid gap-1 text-sm font-medium">
              {t('awareness.fields.contact')}
              <input
                className="input"
                type="email"
                value={form.reporter_contact}
                onChange={(e) => setForm((prev) => ({ ...prev, reporter_contact: e.target.value }))}
              />
            </label>
          )}
          <div>
            <button type="submit" className="btn-primary" disabled={reportMutation.isPending}>
              {reportMutation.isPending ? t('common.loading') : t('awareness.submitReport')}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
