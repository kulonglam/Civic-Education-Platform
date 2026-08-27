import { describe, expect, it, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MfaSetupCard } from './MfaSetupCard';
import { renderWithProviders } from '../test/utils';

vi.mock('qrcode', () => ({
  default: { toDataURL: vi.fn().mockResolvedValue('data:image/png;base64,QR') },
  toDataURL: vi.fn().mockResolvedValue('data:image/png;base64,QR'),
}));

describe('MfaSetupCard', () => {
  it('shows a QR code and setup key during enrollment', async () => {
    renderWithProviders(
      <MfaSetupCard
        enabled={false}
        required
        setup={{ secret: 'JBSWY3DPEHPK3PXP', provisioning_uri: 'otpauth://totp/test' }}
        code=""
        busy=""
        onStart={() => {}}
        onCodeChange={() => {}}
        onConfirm={(e) => e.preventDefault()}
      />,
    );
    expect(screen.getByText(/scan this QR code/i)).toBeInTheDocument();
    expect(screen.getByText('JBSWY3DPEHPK3PXP')).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByRole('img', { name: /qr code/i })).toHaveAttribute('src', 'data:image/png;base64,QR');
    });
  });

  it('starts setup when MFA is required but not enabled', async () => {
    const onStart = vi.fn();
    renderWithProviders(
      <MfaSetupCard
        enabled={false}
        required
        setup={null}
        code=""
        busy=""
        onStart={onStart}
        onCodeChange={() => {}}
        onConfirm={(e) => e.preventDefault()}
      />,
    );
    await userEvent.click(screen.getByRole('button', { name: /set up authenticator/i }));
    expect(onStart).toHaveBeenCalled();
  });
});
