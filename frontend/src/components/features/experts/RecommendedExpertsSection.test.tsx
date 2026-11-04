import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { expertsService } from '@/services/experts.service';
import { assessmentsService } from '@/services/assessments.service';

import { RecommendedExpertsSection } from './RecommendedExpertsSection';

vi.mock('@/services/experts.service', () => ({
  expertsService: { getRecommendedExperts: vi.fn(), submitConsultation: vi.fn() },
}));
vi.mock('@/services/assessments.service', () => ({ assessmentsService: { get: vi.fn() } }));

const recommendation = {
  expert: {
    id: 'expert-1',
    fullName: 'Chuyên gia thử nghiệm',
    title: 'Chuyên gia thuế',
    organization: 'Đơn vị tư vấn',
    avatarUrl: null,
    bio: 'Hồ sơ thử nghiệm',
    specializations: ['Thuế'],
    partnerType: 'tax_consultant' as const,
    servicesOffered: ['Tư vấn thuế'],
    location: 'Toàn quốc',
    experienceYears: 15,
    consultationFeeText: 'Từ 2.500.000 đ / hồ sơ',
    isVerified: false,
  },
  match_reason: 'Phù hợp để rà soát tổng thể.',
};

describe('RecommendedExpertsSection', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(assessmentsService.get).mockResolvedValue({
      id: 'case-1',
      questionnaireVersion: 'v1',
      contentStatus: 'draft',
      answers: {
        businessType: 'company', registrationStatus: 'unknown', householdGoal: 'unknown',
        goal: 'unknown', establishedYear: null, revenueStatus: 'unknown', revenueStartedYear: null,
        filingStatus: 'unknown', discrepancyStatus: 'unknown', recordsStatus: 'unknown',
        taxNoticeStatus: 'unknown', laborInsuranceStatus: 'unknown', assetsInventoryStatus: 'unknown',
        receivablesPayablesStatus: 'unknown',
      },
      summary: { scope: 'b2', knownFacts: [], unknownFacts: [], reviewReasons: [], notice: '' },
      checklist: [],
      createdAt: '', updatedAt: '', expiresAt: '',
    });
  });

  it('shows a recommendation and opens its consultation form from the connect button', async () => {
    vi.mocked(expertsService.getRecommendedExperts).mockResolvedValue([recommendation]);

    render(<RecommendedExpertsSection assessmentId="case-1" initialNotes="Thông tin cần tra cứu" />);

    expect(await screen.findByRole('heading', { name: 'Chuyên gia thử nghiệm' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Kết nối với hồ sơ này' }));
    expect(await screen.findByRole('dialog')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Thông tin cần tra cứu')).toBeInTheDocument();
    expect(expertsService.getRecommendedExperts).toHaveBeenCalledWith('case-1', expect.any(AbortSignal));
  });
});
