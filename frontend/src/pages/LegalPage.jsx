import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

function LegalPage({ type }) {
  const { t } = useTranslation();
  const baseKey = `legal.${type}`;
  const sections = t(`${baseKey}.sections`, { returnObjects: true });

  return (
    <article className="mx-auto max-w-3xl">
      <nav className="mb-6 text-sm text-gray-500 dark:text-slate-400">
        <Link to="/" className="text-brand-600 hover:underline dark:text-brand-400">
          {t('nav.home')}
        </Link>
        <span className="mx-2">/</span>
        <span>{t(`${baseKey}.title`)}</span>
      </nav>

      <header className="mb-8 border-b border-gray-200 pb-6 dark:border-slate-700">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-slate-100">
          {t(`${baseKey}.title`)}
        </h1>
        <p className="mt-2 text-sm text-gray-500 dark:text-slate-400">
          {t(`${baseKey}.lastUpdated`)}
        </p>
        <p className="mt-4 text-gray-600 dark:text-slate-300">{t(`${baseKey}.intro`)}</p>
      </header>

      <div className="space-y-8">
        {Array.isArray(sections) &&
          sections.map((section) => (
            <section key={section.title}>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
                {section.title}
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-gray-600 dark:text-slate-400">
                {section.body}
              </p>
            </section>
          ))}
      </div>
    </article>
  );
}

export function PrivacyPage() {
  return <LegalPage type="privacy" />;
}

export function TermsPage() {
  return <LegalPage type="terms" />;
}

export function ContactPage() {
  const { t } = useTranslation();

  return (
    <article className="mx-auto max-w-3xl">
      <nav className="mb-6 text-sm text-gray-500 dark:text-slate-400">
        <Link to="/" className="text-brand-600 hover:underline dark:text-brand-400">
          {t('nav.home')}
        </Link>
        <span className="mx-2">/</span>
        <span>{t('legal.contact.title')}</span>
      </nav>

      <header className="mb-8 border-b border-gray-200 pb-6 dark:border-slate-700">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-slate-100">
          {t('legal.contact.title')}
        </h1>
        <p className="mt-4 text-gray-600 dark:text-slate-300">{t('legal.contact.intro')}</p>
      </header>

      <div className="card space-y-6">
        <section>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
            {t('legal.contact.supportTitle')}
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-gray-600 dark:text-slate-400">
            {t('legal.contact.supportBody')}
          </p>
          <a
            href="mailto:support@civiced.org"
            className="mt-3 inline-block font-semibold text-brand-700 hover:underline dark:text-brand-300"
          >
            support@civiced.org
          </a>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
            {t('legal.contact.orgTitle')}
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-gray-600 dark:text-slate-400">
            {t('legal.contact.orgBody')}
          </p>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
            {t('legal.contact.legalTitle')}
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-gray-600 dark:text-slate-400">
            {t('legal.contact.legalBody')}
          </p>
          <div className="mt-3 flex flex-wrap gap-4 text-sm font-semibold">
            <Link to="/privacy" className="text-brand-700 hover:underline dark:text-brand-300">
              {t('footer.privacy')}
            </Link>
            <Link to="/terms" className="text-brand-700 hover:underline dark:text-brand-300">
              {t('footer.terms')}
            </Link>
          </div>
        </section>
      </div>
    </article>
  );
}
