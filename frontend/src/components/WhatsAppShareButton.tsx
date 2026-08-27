import { useTranslation } from 'react-i18next';
import { whatsappShareUrl } from '../lib/whatsapp';

export function WhatsAppShareButton({
  title,
  path = '',
  className = '',
}: {
  title: string;
  path?: string;
  className?: string;
}) {
  const { t } = useTranslation();
  const origin = typeof window !== 'undefined' ? window.location.origin : '';
  const url = path ? `${origin}${path}` : origin;
  const href = whatsappShareUrl(title, url);

  return (
    <a
      href={href}
      className={`btn-secondary text-sm ${className}`}
      target="_blank"
      rel="noopener noreferrer"
    >
      {t('whatsapp.share')}
    </a>
  );
}
