import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { expertsService } from '@/services/experts.service';

import { ExpertsWorkspace } from './ExpertsWorkspace';

vi.mock('@/services/experts.service', () => ({
  expertsService: { getExperts: vi.fn(), submitConsultation: vi.fn() },
}));
vi.mock('@/services/assessments.service', () => ({ assessmentsService: { get: vi.fn() } }));

const expert = {
  id: 'firm-1',
  fullName: 'Công ty Kế toán Minh Khang',
  title: 'Công ty dịch vụ kế toán',
  organization: 'Minh Khang',
  avatarUrl: null,
  bio: 'Rà soát hồ sơ thuế.',
  specializations: ['Sổ sách kế toán'],
  partnerType: 'accounting_firm' as const,
  servicesOffered: ['Dọn sổ sách', 'Quyết toán giải thể'],
  location: 'Hà Nội',
  experienceYears: 15,
  consultationFeeText: 'Từ 3.500.000 đ / hồ sơ',
  isVerified: false,
};

describe('ExpertsWorkspace', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    window.history.replaceState({}, '', '/chuyen-gia');
  });

  it('filters the directory by partner type and shows partner services', async () => {
    vi.mocked(expertsService.getExperts).mockResolvedValue([expert]);
    render(<ExpertsWorkspace initialFilters={{}} />);

    expect(await screen.findByText('Công ty Kế toán Minh Khang')).toBeInTheDocument();
    expect(screen.getAllByText('Công ty kế toán')).toHaveLength(2);
    expect(screen.getByText('Dọn sổ sách · Quyết toán giải thể')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Người làm kế toán' }));
    await waitFor(() => expect(expertsService.getExperts).toHaveBeenLastCalledWith(
      { q: '', specialization: '', location: '', partnerType: 'accountant' },
      expect.any(AbortSignal),
    ));
    expect(window.location.search).toContain('partnerType=accountant');
  });
});
