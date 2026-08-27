export function whatsappShareUrl(text, url) {
  const parts = [text, url].filter(Boolean).join('\n');
  return `https://wa.me/?text=${encodeURIComponent(parts)}`;
}

export function whatsappClickToChatUrl(displayNumber) {
  if (!displayNumber) return '';
  const digits = String(displayNumber).replace(/[^\d]/g, '');
  return digits ? `https://wa.me/${digits}` : '';
}
