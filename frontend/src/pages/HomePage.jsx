import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import {
  AcademicCap,
  BookOpen,
  CloudArrowDown,
  ShieldCheck,
} from '../components/Icons';

function HomePage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { isOrgAdmin } = useOrganization();

  const features = [
    {
      title: t('home.featureLearnTitle'),
      text: t('home.featureLearnText'),
      Icon: BookOpen,
    },
    {
      title: t('home.featureQuizTitle'),
      text: t('home.featureQuizText'),
      Icon: AcademicCap,
    },
    {
      title: t('home.featureForumTitle'),
      text: t('home.featureForumText'),
      Icon: ShieldCheck,
    },
  ];

  const steps = [
    { step: '01', title: t('home.step1Title'), text: t('home.step1Text') },
    { step: '02', title: t('home.step2Title'), text: t('home.step2Text') },
    { step: '03', title: t('home.step3Title'), text: t('home.step3Text') },
  ];

  const trustItems = [
    t('home.trustArticles'),
    t('home.trustQuizzes'),
    t('home.trustOffline'),
    t('home.trustLanguages'),
  ];

  const topics = [
    { label: t('home.topicConstitution'), to: '/articles?category=constitution' },
    { label: t('home.topicGovernance'), to: '/articles?category=governance' },
    { label: t('home.topicElections'), to: '/articles?category=elections' },
    { label: t('home.topicPeacebuilding'), to: '/articles?category=peacebuilding' },
  ];

  return (
    <div>
      {/* Full-bleed hero: photo plane + headline, support, CTAs (brand lives in navbar) */}
      <section
        aria-labelledby="home-hero-title"
        className="relative isolate min-h-[min(92vh,52rem)] overflow-hidden bg-brand-950 text-white"
      >
        <img
          src="/hero-civic.jpg"
          alt={t('home.heroImageAlt')}
          className="absolute inset-0 h-full w-full object-cover object-[center_28%]"
          fetchPriority="high"
        />
        <div
          className="absolute inset-0 bg-[linear-gradient(115deg,rgba(2,44,34,0.92)_0%,rgba(6,78,59,0.78)_48%,rgba(4,120,87,0.55)_100%)]"
          aria-hidden="true"
        />
        <div
          className="pointer-events-none absolute -right-24 top-10 h-[28rem] w-[28rem] rounded-full bg-brand-400/15 blur-3xl animate-soft-pulse"
          aria-hidden="true"
        />

        <div className="relative prose-panel flex min-h-[min(92vh,52rem)] flex-col justify-center py-16 sm:py-20">
          <div className="max-w-3xl">
            {user && (
              <p className="animate-fade-up text-sm font-medium text-brand-200">
                {t('home.welcomeBack', { name: user.first_name })}
              </p>
            )}

            <h1
              id="home-hero-title"
              className={`animate-fade-up-delay font-display text-4xl font-semibold leading-[1.1] text-white sm:text-5xl lg:text-6xl ${user ? 'mt-5' : ''}`}
            >
              {t('home.heroTitle')}
            </h1>
            <p className="animate-fade-up-late mt-5 max-w-xl text-lg leading-relaxed text-brand-100/95">
              {t('home.heroSubtitle')}
            </p>

            <div className="animate-fade-up-late mt-9 flex flex-wrap gap-3">
              {user ? (
                <>
                  <Link
                    to="/articles"
                    className="btn bg-white text-brand-800 shadow-lift hover:bg-brand-50"
                  >
                    {t('home.continueLearning')}
                  </Link>
                  <Link
                    to="/quizzes"
                    className="btn border border-white/35 bg-white/5 text-white backdrop-blur hover:bg-white/10"
                  >
                    {t('home.takeQuiz')}
                  </Link>
                  {isOrgAdmin && (
                    <Link
                      to="/dashboard"
                      className="btn border border-white/35 bg-white/5 text-white backdrop-blur hover:bg-white/10"
                    >
                      {t('home.goToDashboard')}
                    </Link>
                  )}
                </>
              ) : (
                <>
                  <Link
                    to="/register"
                    className="btn bg-white text-brand-800 shadow-lift hover:bg-brand-50"
                  >
                    {t('home.getStarted')}
                  </Link>
                  <Link
                    to="/register?type=organization"
                    className="btn border border-white/35 bg-white/5 text-white backdrop-blur hover:bg-white/10"
                  >
                    {t('home.setupOrganization')}
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Proof layer: capabilities + topic entry points (below the fold) */}
      <section
        aria-labelledby="home-trust-label"
        className="border-b border-ink-100 bg-ink-50/60 dark:border-slate-800 dark:bg-slate-900/40"
      >
        <div className="prose-panel py-10 sm:py-12">
          <p id="home-trust-label" className="eyebrow">
            {t('home.trustLabel')}
          </p>
          <ul className="trust-strip mt-4">
            {trustItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-baseline sm:gap-6">
            <p className="text-sm font-semibold text-ink-800 dark:text-slate-200">
              {t('home.topicsLabel')}
            </p>
            <ul className="topic-links">
              {topics.map((topic) => (
                <li key={topic.label}>
                  <Link to={topic.to}>{topic.label}</Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <div className="prose-panel space-y-24 py-16 sm:py-20">
        <section aria-labelledby="home-features-title">
          <div className="max-w-2xl">
            <h2 id="home-features-title" className="section-heading">
              {t('home.featuresTitle')}
            </h2>
            <p className="section-lead">{t('home.featuresSubtitle')}</p>
          </div>
          <div className="mt-10 grid gap-10 sm:grid-cols-3">
            {features.map((f) => (
              <div key={f.title} className="group">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-100 text-brand-700 transition-transform duration-300 group-hover:-translate-y-0.5 dark:bg-brand-900/50 dark:text-brand-300">
                  <f.Icon className="h-6 w-6" />
                </div>
                <h3 className="font-display text-xl font-semibold text-ink-900 dark:text-slate-100">
                  {f.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-ink-700/75 dark:text-slate-400">
                  {f.text}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section aria-labelledby="home-steps-title">
          <div className="max-w-2xl">
            <h2 id="home-steps-title" className="section-heading">
              {t('home.howItWorksTitle')}
            </h2>
            <p className="section-lead">{t('home.howItWorksSubtitle')}</p>
          </div>
          <ol className="mt-12 grid gap-8 border-t border-ink-100 pt-10 dark:border-slate-800 sm:grid-cols-3">
            {steps.map(({ step, title, text }) => (
              <li key={step}>
                <span className="font-display text-sm font-semibold tracking-widest text-brand-600 dark:text-brand-400">
                  {step}
                </span>
                <h3 className="mt-3 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">
                  {title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-ink-700/75 dark:text-slate-400">
                  {text}
                </p>
              </li>
            ))}
          </ol>
        </section>

        <section
          aria-labelledby="home-audiences-title"
          className="grid gap-12 lg:grid-cols-2 lg:gap-16"
        >
          <div>
            <p className="text-sm font-semibold tracking-wide text-brand-700 dark:text-brand-400">
              {t('home.audienceCitizenLabel')}
            </p>
            <h2
              id="home-audiences-title"
              className="mt-2 font-display text-2xl font-semibold text-ink-900 dark:text-slate-100 sm:text-3xl"
            >
              {t('home.audienceCitizenTitle')}
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-ink-700/80 dark:text-slate-400">
              {t('home.audienceCitizenText')}
            </p>
            {!user && (
              <Link to="/register" className="btn-primary mt-6">
                {t('home.audienceCitizenCta')}
              </Link>
            )}
          </div>
          <div>
            <p className="text-sm font-semibold tracking-wide text-brand-700 dark:text-brand-400">
              {t('home.audienceOrgLabel')}
            </p>
            <h2 className="mt-2 font-display text-2xl font-semibold text-ink-900 dark:text-slate-100 sm:text-3xl">
              {t('home.audienceOrgTitle')}
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-ink-700/80 dark:text-slate-400">
              {t('home.audienceOrgText')}
            </p>
            {!user && (
              <Link to="/register?type=organization" className="btn-secondary mt-6">
                {t('home.audienceOrgCta')}
              </Link>
            )}
          </div>
        </section>

        <section
          aria-labelledby="home-built-title"
          className="flex flex-col gap-6 border-y border-ink-100 py-12 dark:border-slate-800 sm:flex-row sm:items-center"
        >
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-brand-700 text-white">
            <CloudArrowDown className="h-7 w-7" />
          </div>
          <div>
            <h2
              id="home-built-title"
              className="font-display text-2xl font-semibold text-ink-900 dark:text-slate-100"
            >
              {t('home.builtForTitle')}
            </h2>
            <p className="mt-2 max-w-3xl text-sm leading-relaxed text-ink-700/80 dark:text-slate-400">
              {t('home.builtForText')}
            </p>
          </div>
        </section>

        {!user && (
          <section className="relative overflow-hidden rounded-[2rem] bg-brand-900 px-8 py-14 text-center text-white sm:px-12">
            <div
              className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(52,211,153,0.25),transparent_55%)]"
              aria-hidden="true"
            />
            <div className="relative">
              <h2 className="font-display text-3xl font-semibold sm:text-4xl">
                {t('home.finalCtaTitle')}
              </h2>
              <p className="mx-auto mt-3 max-w-xl text-brand-100/90">
                {t('home.finalCtaText')}
              </p>
              <div className="mt-8 flex flex-wrap justify-center gap-3">
                <Link to="/register" className="btn bg-white text-brand-800 hover:bg-brand-50">
                  {t('home.getStarted')}
                </Link>
                <Link
                  to="/login"
                  className="btn border border-white/30 text-white hover:bg-white/10"
                >
                  {t('nav.login')}
                </Link>
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

export { HomePage };
