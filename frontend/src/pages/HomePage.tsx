import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  AcademicCap,
  BookOpen,
  ChatBubble,
  CloudArrowDown,
  FileText,
  Calendar,
  Eye,
  Megaphone,
  ShieldCheck,
} from '../components/Icons';
import { RecommendationsSection } from '../components/RecommendationsSection';
import { CIVIC_PHOTOS, HERO_PHOTO, photoForTopic } from '../lib/civicPhotos';

function HomePage() {
  const { t } = useTranslation();
  const { user } = useAuth();

  const features = [
    {
      title: t('home.featureLearnTitle'),
      text: t('home.featureLearnText'),
      Icon: BookOpen,
    },
    {
      title: t('home.featureNewsTitle'),
      text: t('home.featureNewsText'),
      Icon: FileText,
    },
    {
      title: t('home.featureEventsTitle'),
      text: t('home.featureEventsText'),
      Icon: Calendar,
    },
    {
      title: t('home.featureAwarenessTitle'),
      text: t('home.featureAwarenessText'),
      Icon: Eye,
    },
    {
      title: t('home.featureQuizTitle'),
      text: t('home.featureQuizText'),
      Icon: AcademicCap,
    },
    {
      title: t('home.featureTutorTitle'),
      text: t('home.featureTutorText'),
      Icon: ChatBubble,
    },
    {
      title: t('home.featureEngageTitle'),
      text: t('home.featureEngageText'),
      Icon: Megaphone,
    },
    {
      title: t('home.featureForumTitle'),
      text: t('home.featureForumText'),
      Icon: ShieldCheck,
    },
    {
      title: t('home.featureAccessTitle'),
      text: t('home.featureAccessText'),
      Icon: Eye,
    },
  ];

  const steps = [
    { step: '01', title: t('home.step1Title'), text: t('home.step1Text') },
    { step: '02', title: t('home.step2Title'), text: t('home.step2Text') },
    { step: '03', title: t('home.step3Title'), text: t('home.step3Text') },
  ];

  const trustItems = [
    t('home.trustArticles'),
    t('home.trustNews'),
    t('home.trustEvents'),
    t('home.trustAwareness'),
    t('home.trustQuizzes'),
    t('home.trustTutor'),
    t('home.trustEngage'),
    t('home.trustOffline'),
    t('home.trustLanguages'),
  ];

  const topics = [
    { label: t('home.topicConstitution'), to: '/articles?category=constitution', slug: 'constitution' },
    { label: t('home.topicHumanRights'), to: '/articles?category=human-rights', slug: 'human-rights' },
    { label: t('home.topicCitizenResponsibilities'), to: '/articles?category=citizen-responsibilities', slug: 'citizen-responsibilities' },
    { label: t('home.topicGovernmentStructure'), to: '/articles?category=government-structure', slug: 'government-structure' },
    { label: t('home.topicGovernance'), to: '/articles?category=governance', slug: 'governance' },
    { label: t('home.topicElections'), to: '/articles?category=elections', slug: 'elections' },
    { label: t('home.topicRuleOfLaw'), to: '/articles?category=rule-of-law', slug: 'rule-of-law' },
    { label: t('home.topicPeacebuilding'), to: '/articles?category=peacebuilding', slug: 'peacebuilding' },
    { label: t('home.topicGenderEquality'), to: '/articles?category=gender-equality', slug: 'gender-equality' },
    { label: t('home.topicAntiCorruption'), to: '/articles?category=anti-corruption', slug: 'anti-corruption' },
    { label: t('home.topicPublicParticipation'), to: '/articles?category=public-participation', slug: 'public-participation' },
    { label: t('home.topicMediaMisinformation'), to: '/articles?category=media-misinformation', slug: 'media-misinformation' },
    { label: t('home.topicDigitalCitizenship'), to: '/articles?category=digital-citizenship', slug: 'digital-citizenship' },
    { label: t('home.topicCommunityLeadership'), to: '/articles?category=community-leadership', slug: 'community-leadership' },
    { label: t('home.topicConflictResolution'), to: '/articles?category=conflict-resolution', slug: 'conflict-resolution' },
  ];

  return (
    <div>
      {/* Full-bleed hero: photo plane + headline, support, CTAs (brand lives in navbar) */}
      <section
        aria-labelledby="home-hero-title"
        className="relative isolate min-h-[min(68vh,34rem)] overflow-hidden bg-brand-950 text-white sm:min-h-[min(88vh,48rem)]"
      >
        <img
          src={HERO_PHOTO}
          alt={t('home.heroImageAlt')}
          width={1920}
          height={1080}
          sizes="100vw"
          decoding="sync"
          className="absolute inset-0 h-full w-full object-cover object-[center_42%]"
          fetchPriority="high"
        />
        <div
          className="absolute inset-0 bg-[linear-gradient(105deg,rgba(0,0,0,0.52)_0%,rgba(0,0,0,0.22)_48%,rgba(0,0,0,0.08)_100%)]"
          aria-hidden="true"
        />

        <div className="relative prose-panel flex min-h-[min(68vh,34rem)] flex-col justify-center py-12 sm:min-h-[min(88vh,48rem)] sm:py-20">
          <div className="max-w-3xl">
            {user && (
              <p className="animate-fade-up text-sm font-medium text-white/90 drop-shadow-[0_1px_8px_rgba(0,0,0,0.5)]">
                {t('home.welcomeBack', { name: user.first_name })}
              </p>
            )}

            <h1
              id="home-hero-title"
              className={`animate-fade-up-delay font-display text-hero text-white drop-shadow-[0_2px_14px_rgba(0,0,0,0.55)] ${user ? 'mt-5' : ''}`}
            >
              {t('home.heroTitle')}
            </h1>
            <p className="animate-fade-up-late mt-5 max-w-xl text-hero-sub text-white/95 drop-shadow-[0_1px_10px_rgba(0,0,0,0.5)]">
              {t('home.heroSubtitle')}
            </p>

            <div className="animate-fade-up-late mt-8 flex flex-col gap-3 sm:mt-9 sm:flex-row sm:flex-wrap [&_.btn]:w-full [&_.btn]:justify-center sm:[&_.btn]:w-auto">
              {user ? (
                <>
                  <Link
                    to="/articles"
                    className="btn bg-white text-brand-800 shadow-lift hover:bg-brand-50"
                  >
                    {t('home.continueLearning')}
                  </Link>
                  <Link
                    to="/tutor"
                    className="btn border border-white/35 bg-white/5 text-white backdrop-blur hover:bg-white/10"
                  >
                    {t('home.askTutor')}
                  </Link>
                  <Link
                    to="/dashboard"
                    className="btn border border-white/35 bg-white/5 text-white backdrop-blur hover:bg-white/10"
                  >
                    {t('home.myProgress')}
                  </Link>
                  <Link
                    to="/engage"
                    className="btn border border-white/35 bg-white/5 text-white backdrop-blur hover:bg-white/10"
                  >
                    {t('home.civicAction')}
                  </Link>
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
                  <Link
                    to="/news"
                    className="btn border border-white/35 bg-white/5 text-white backdrop-blur hover:bg-white/10"
                  >
                    {t('home.browseNews')}
                  </Link>
                  <Link
                    to="/events"
                    className="btn border border-white/35 bg-white/5 text-white backdrop-blur hover:bg-white/10"
                  >
                    {t('home.browseEvents')}
                  </Link>
                  <Link
                    to="/awareness"
                    className="btn border border-white/35 bg-white/5 text-white backdrop-blur hover:bg-white/10"
                  >
                    {t('home.browseAwareness')}
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {user && (
        <section className="prose-panel py-10">
          <RecommendationsSection />
        </section>
      )}

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
          <div className="mt-8">
            <p className="text-sm font-semibold text-ink-800 dark:text-slate-200">
              {t('home.topicsLabel')}
            </p>
            <ul className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
              {topics.map((topic) => (
                <li key={topic.slug}>
                  <Link
                    to={topic.to}
                    className="group relative block overflow-hidden rounded-2xl shadow-soft ring-1 ring-ink-100 dark:ring-slate-700"
                  >
                    <img
                      src={photoForTopic(topic.slug)}
                      alt=""
                      className="h-28 w-full object-cover transition duration-300 group-hover:scale-[1.04] sm:h-32"
                    />
                    <span className="absolute inset-x-0 bottom-0 h-2/3 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
                    <span className="absolute inset-x-0 bottom-0 p-2.5 text-sm font-semibold leading-snug text-white">
                      {topic.label}
                    </span>
                  </Link>
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
          <div className="mt-10 grid gap-10 sm:grid-cols-2 lg:grid-cols-3">
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
            <img
              src={CIVIC_PHOTOS.womenFlags}
              alt={t('photos.womenFlags')}
              className="mb-5 h-48 w-full rounded-2xl object-cover shadow-soft sm:h-56"
            />
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
            <img
              src={CIVIC_PHOTOS.ceremony}
              alt={t('photos.ceremony')}
              className="mb-5 h-48 w-full rounded-2xl object-cover shadow-soft sm:h-56"
            />
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
          className="overflow-hidden rounded-3xl border border-ink-100 dark:border-slate-800 sm:grid sm:grid-cols-[minmax(0,18rem)_1fr]"
        >
          <img
            src={CIVIC_PHOTOS.crowdFlags}
            alt={t('photos.crowdFlags')}
            className="h-44 w-full object-cover sm:h-full"
          />
          <div className="flex flex-col justify-center gap-3 p-6 sm:p-8">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-brand-700 text-white">
              <CloudArrowDown className="h-7 w-7" />
            </div>
            <h2
              id="home-built-title"
              className="font-display text-2xl font-semibold text-ink-900 dark:text-slate-100"
            >
              {t('home.builtForTitle')}
            </h2>
            <p className="max-w-3xl text-sm leading-relaxed text-ink-700/80 dark:text-slate-400">
              {t('home.builtForText')}
            </p>
          </div>
        </section>

        {!user && (
          <section className="relative overflow-hidden rounded-3xl bg-ink-950 px-5 py-10 text-center text-white sm:rounded-[2rem] sm:px-12 sm:py-14">
            <img
              src={CIVIC_PHOTOS.independence}
              alt=""
              className="absolute inset-0 h-full w-full object-cover"
            />
            <div
              className="absolute inset-0 bg-black/40"
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
