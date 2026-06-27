import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Pagination } from '../components/Pagination';
import { EmptyState, PageHeader } from '../components/ui';
import { Trophy } from '../components/Icons';
import { queryKeys } from '../lib/queryKeys';
import { quizService } from '../lib/services';
import { formatDate } from '../lib/format';

const PAGE_SIZE = 20;

function CertCardSkeleton() {
  return (
    <div className="card space-y-3">
      <div className="flex items-start justify-between">
        <div className="skeleton h-12 w-12 rounded-full" />
        <div className="skeleton h-5 w-28 rounded-full" />
      </div>
      <div className="skeleton h-5 w-3/4" />
      <div className="skeleton h-4 w-1/2" />
      <div className="skeleton mt-2 h-9 w-full" />
    </div>
  );
}

export function CertificatesPage() {
  const { t } = useTranslation();
  const [page, setPage] = useState(1);
  const [downloading, setDownloading] = useState(null);

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.certificates({ page }),
    queryFn: async () => {
      const { data: res } = await quizService.certificates({ page: String(page) });
      return res;
    },
  });

  const certificates = data?.results ?? [];
  const totalCount = data?.count ?? 0;

  const download = async (cert) => {
    setDownloading(cert.id);
    try {
      const { data: res } = await quizService.downloadCertificate(cert.id);
      window.open(res.download_url, '_blank');
    } catch {
      if (cert.pdf_url) window.open(cert.pdf_url, '_blank');
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div>
      <PageHeader
        title={t('quizzes.certificates')}
        action={
          <Link to="/quizzes" className="btn-secondary">
            {t('common.back')}
          </Link>
        }
      />

      {isLoading ? (
        <div className="grid gap-6 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => <CertCardSkeleton key={i} />)}
        </div>
      ) : certificates.length === 0 ? (
        <EmptyState>{t('common.noResults')}</EmptyState>
      ) : (
        <>
          <div className="grid gap-6 sm:grid-cols-2">
            {certificates.map((cert) => (
              <div
                key={cert.id}
                className="relative overflow-hidden rounded-2xl border-2 border-brand-200 bg-white p-6 shadow-sm dark:border-brand-800 dark:bg-slate-800"
              >
                {/* Decorative corner accent */}
                <div className="absolute -right-6 -top-6 h-20 w-20 rounded-full bg-brand-50 dark:bg-brand-900/30" />
                <div className="absolute -right-3 -top-3 h-12 w-12 rounded-full bg-brand-100 dark:bg-brand-900/50" />

                <div className="relative flex items-start justify-between gap-3">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-600 dark:bg-brand-900/50 dark:text-brand-300">
                    <Trophy className="h-6 w-6" />
                  </div>
                  <span className="badge bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
                    #{cert.certificate_number}
                  </span>
                </div>

                <h3 className="relative mt-4 text-lg font-bold text-gray-900 dark:text-slate-100">
                  {cert.quiz_title}
                </h3>
                <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
                  {t('quizzes.issued')}: {formatDate(cert.issue_date)}
                </p>

                <div className="relative mt-2 flex items-center gap-2">
                  <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
                    <svg className="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <path d="M20 6L9 17l-5-5" />
                    </svg>
                    {t('quizzes.passed')}
                  </span>
                </div>

                <button
                  type="button"
                  className="btn-primary relative mt-5 w-full"
                  onClick={() => download(cert)}
                  disabled={downloading === cert.id}
                >
                  {downloading === cert.id ? t('common.loading') : t('quizzes.download')}
                </button>
              </div>
            ))}
          </div>
          <Pagination
            page={page}
            totalCount={totalCount}
            pageSize={PAGE_SIZE}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  );
}
