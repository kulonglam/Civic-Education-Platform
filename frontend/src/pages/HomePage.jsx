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
      color: 'bg-brand-50 text-brand-600 dark:bg-brand-900/40 dark:text-brand-300',
    },
    {
      title: t('home.featureQuizTitle'),
      text: t('home.featureQuizText'),
      Icon: AcademicCap,
      color: 'bg-brand-100 text-brand-700 dark:bg-brand-900/50 dark:text-brand-200',
    },
    {
      title: t('home.featureForumTitle'),
      text: t('home.featureForumText'),
      Icon: ShieldCheck,
      color: 'bg-brand-200 text-brand-800 dark:bg-brand-800/40 dark:text-brand-100',
    },
  ];

  const trustItems = [
    t('home.trustArticles'),
    t('home.trustQuizzes'),
    t('home.trustOffline'),
    t('home.trustLanguages'),
  ];

  const steps = [
    { step: '1', title: t('home.step1Title'), text: t('home.step1Text') },
    { step: '2', title: t('home.step2Title'), text: t('home.step2Text') },
    { step: '3', title: t('home.step3Title'), text: t('home.step3Text') },
  ];

  return (
    <div className="space-y-20 pb-4">
      {/* Hero */}
      <section
        aria-labelledby="home-hero-title"
        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-brand-700 to-brand-900 px-6 py-16 text-center text-white sm:px-12"
      >
        <div
          className="pointer-events-none absolute inset-0 opacity-10"
          aria-hidden="true"
          style={{
            backgroundImage:
              'radial-gradient(circle at 20% 50%, white 1px, transparent 1px), radial-gradient(circle at 80% 20%, white 1px, transparent 1px)',
            backgroundSize: '48px 48px',
          }}
        />
        <div className="relative">
          {user && (
            <p className="mb-3 text-sm font-medium text-brand-200">
              {t('home.welcomeBack', { name: user.first_name })}
            </p>
          )}
          <h1
            id="home-hero-title"
            className="mx-auto max-w-3xl text-4xl font-extrabold leading-tight sm:text-5xl"
          >
            {t('home.heroTitle')}
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-brand-100">{t('home.heroSubtitle')}</p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            {user ? (
              <>
                <Link to="/articles" className="btn bg-white text-brand-700 hover:bg-brand-50">
                  {t('home.continueLearning')}
                </Link>
                <Link to="/quizzes" className="btn border border-white/40 text-white hover:bg-white/10">
                  {t('home.takeQuiz')}
                </Link>
                {isOrgAdmin && (
                  <Link to="/dashboard" className="btn border border-white/40 text-white hover:bg-white/10">
                    {t('home.goToDashboard')}
                  </Link>
                )}
              </>
            ) : (
              <>
                <Link to="/register" className="btn bg-white text-brand-700 hover:bg-brand-50">
                  {t('home.getStarted')}
                </Link>
                <Link
                  to="/register?type=organization"
                  className="btn border border-white/40 text-white hover:bg-white/10"
                >
                  {t('home.setupOrganization')}
                </Link>
              </>
            )}
            <Link to="/articles" className="btn border border-white/40 text-white hover:bg-white/10">
              {t('home.browseArticles')}
            </Link>
          </div>
        </div>
      </section>

      {/* Trust strip */}
      <section aria-label={t('home.trustLabel')} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {trustItems.map((item) => (
          <div
            key={item}
            className="flex items-center justify-center rounded-xl border border-brand-100 bg-brand-50/60 px-4 py-3 text-center text-sm font-medium text-brand-800 dark:border-brand-900/50 dark:bg-brand-950/40 dark:text-brand-200"
          >
            {item}
          </div>
        ))}
      </section>

      {/* Features */}
      <section aria-labelledby="home-features-title">
        <h2 id="home-features-title" className="sr-only">
          {t('home.featuresTitle')}
        </h2>
        <div className="grid gap-6 sm:grid-cols-3">
          {features.map((f) => (
            <div key={f.title} className="card text-center">
              <div
                className={`mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full ${f.color}`}
              >
                <f.Icon className="h-7 w-7" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-slate-100">{f.title}</h3>
              <p className="mt-2 text-sm text-gray-600 dark:text-slate-400">{f.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section aria-labelledby="home-steps-title" className="card">
        <h2 id="home-steps-title" className="text-center text-2xl font-bold text-gray-900 dark:text-slate-100">
          {t('home.howItWorksTitle')}
        </h2>
        <p className="mx-auto mt-2 max-w-2xl text-center text-sm text-gray-600 dark:text-slate-400">
          {t('home.howItWorksSubtitle')}
        </p>
        <ol className="mt-10 grid gap-8 sm:grid-cols-3">
          {steps.map(({ step, title, text }) => (
            <li key={step} className="text-center">
              <span className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-brand-600 text-sm font-bold text-white">
                {step}
              </span>
              <h3 className="mt-4 font-semibold text-gray-900 dark:text-slate-100">{title}</h3>
              <p className="mt-2 text-sm text-gray-600 dark:text-slate-400">{text}</p>
            </li>
          ))}
        </ol>
      </section>

      {/* Audiences */}
      <section aria-labelledby="home-audiences-title" className="grid gap-6 lg:grid-cols-2">
        <div className="card flex flex-col">
          <p className="text-xs font-semibold uppercase tracking-wide text-brand-600 dark:text-brand-400">
            {t('home.audienceCitizenLabel')}
          </p>
          <h2
            id="home-audiences-title"
            className="mt-2 text-xl font-bold text-gray-900 dark:text-slate-100"
          >
            {t('home.audienceCitizenTitle')}
          </h2>
          <p className="mt-3 flex-1 text-sm text-gray-600 dark:text-slate-400">
            {t('home.audienceCitizenText')}
          </p>
          {!user && (
            <Link to="/register" className="btn-primary mt-6 w-fit">
              {t('home.audienceCitizenCta')}
            </Link>
          )}
        </div>
        <div className="card flex flex-col border-brand-200 dark:border-brand-900/60">
          <p className="text-xs font-semibold uppercase tracking-wide text-brand-600 dark:text-brand-400">
            {t('home.audienceOrgLabel')}
          </p>
          <h2 className="mt-2 text-xl font-bold text-gray-900 dark:text-slate-100">
            {t('home.audienceOrgTitle')}
          </h2>
          <p className="mt-3 flex-1 text-sm text-gray-600 dark:text-slate-400">
            {t('home.audienceOrgText')}
          </p>
          {!user && (
            <Link to="/register?type=organization" className="btn-secondary mt-6 w-fit">
              {t('home.audienceOrgCta')}
            </Link>
          )}
        </div>
      </section>

      {/* Offline & languages */}
      <section
        aria-labelledby="home-built-title"
        className="flex flex-col items-center gap-6 rounded-3xl border border-gray-200 bg-white px-6 py-10 text-center dark:border-slate-700 dark:bg-slate-800 sm:flex-row sm:text-left"
      >
        <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 dark:bg-brand-900/40 dark:text-brand-300">
          <CloudArrowDown className="h-8 w-8" />
        </div>
        <div className="flex-1">
          <h2 id="home-built-title" className="text-xl font-bold text-gray-900 dark:text-slate-100">
            {t('home.builtForTitle')}
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-slate-400">{t('home.builtForText')}</p>
        </div>
      </section>

      {/* Final CTA */}
      {!user && (
        <section className="rounded-3xl bg-gradient-to-r from-brand-600 to-brand-800 px-6 py-12 text-center text-white">
          <h2 className="text-2xl font-bold">{t('home.finalCtaTitle')}</h2>
          <p className="mx-auto mt-2 max-w-xl text-brand-100">{t('home.finalCtaText')}</p>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <Link to="/register" className="btn bg-white text-brand-700 hover:bg-brand-50">
              {t('home.getStarted')}
            </Link>
            <Link to="/login" className="btn border border-white/40 text-white hover:bg-white/10">
              {t('nav.login')}
            </Link>
          </div>
        </section>
      )}
    </div>
  );
}

export { HomePage };
