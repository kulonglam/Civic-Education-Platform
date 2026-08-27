export function whatsappShareUrl(text?: string | null, url?: string | null) {
  const parts = [text, url].filter(Boolean).join('\n');
  return `https://wa.me/?text=${encodeURIComponent(parts)}`;
}

export function whatsappClickToChatUrl(displayNumber?: string | null) {
  if (!displayNumber) return '';
  const digits = String(displayNumber).replace(/[^\d]/g, '');
  return digits ? `https://wa.me/${digits}` : '';
}
