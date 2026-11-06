import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { assessmentsService } from '@/services/assessments.service';
import { expertsService } from '@/services/experts.service';

import { ConsultationModal } from './ConsultationModal';

vi.mock('@/services/experts.service', () => ({
  expertsService: { submitConsultation: vi.fn() },
}));
vi.mock('@/services/assessments.service', () => ({ assessmentsService: { get: vi.fn() } }));

const expert = {
  id: 'firm-1',
  fullName: 'Công ty Kế toán Minh Khang',
  title: 'Đại lý thuế',
  organization: 'Minh Khang',
  avatarUrl: null,
  bio: 'Hỗ trợ quyết toán.',
  specializations: ['Thuế'],
  partnerType: 'accounting_firm' as const,
  servicesOffered: ['Dọn sổ sách'],
  location: 'Hà Nội',
  experienceYears: 15,
  consultationFeeText: 'Từ 3.500.000 đ / hồ sơ',
  isVerified: false,
};

const assessment = {
  id: 'case-1',
  questionnaireVersion: 'v1',
  contentStatus: 'draft' as const,
  answers: {
    businessType: 'company' as const,
    registrationStatus: 'yes' as const,
    householdGoal: 'unknown' as const,
    goal: 'dissolution' as const,
    establishedYear: 2010,
    revenueStatus: 'unknown' as const,
    revenueStartedYear: null,
    filingStatus: 'unknown' as const,
    discrepancyStatus: 'unknown' as const,
    recordsStatus: 'unknown' as const,
    taxNoticeStatus: 'unknown' as const,
    laborInsuranceStatus: 'unknown' as const,
    assetsInventoryStatus: 'unknown' as const,
    receivablesPayablesStatus: 'unknown' as const,
  },
  summary: {
    scope: 'a3' as const,
    knownFacts: [],
    unknownFacts: [],
    reviewReasons: [],
    notice: '',
  },
  checklist: [
    {
      id: 'item-1',
      code: 'invoice',
      label: 'Hóa đơn',
      status: 'available' as const,
      reviewStatus: 'draft' as const,
      note: null,
    },
  ],
  createdAt: '',
  updatedAt: '',
  expiresAt: '',
};

describe('ConsultationModal', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(assessmentsService.get).mockResolvedValue(assessment);
    vi.mocked(expertsService.submitConsultation).mockResolvedValue({
      id: 'request-1',
      expertId: 'firm-1',
      status: 'pending',
      createdAt: '',
    });
  });

  it('shows the case snapshot and submits requested service with consent', async () => {
    render(<ConsultationModal expert={expert} assessmentId="case-1" open onOpenChange={vi.fn()} />);

    expect(await screen.findByText('Hộ kinh doanh cần rà soát kê khai')).toBeInTheDocument();
    expect(screen.getByText('Từ 3.500.000 đ / hồ sơ')).toBeInTheDocument();
    expect(screen.getByText('Hóa đơn')).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Họ tên'), { target: { value: 'Nguyễn An' } });
    fireEvent.change(screen.getByLabelText('Số điện thoại'), { target: { value: '0912345678' } });
    fireEvent.change(screen.getByPlaceholderText(/Mô tả ngắn tình huống/), {
      target: { value: 'Rà soát số liệu' },
    });
    fireEvent.change(screen.getByLabelText('Dịch vụ cần thực hiện'), {
      target: { value: 'Kiểm tra và giải trình chênh lệch số liệu thuế' },
    });
    // Không gửi khi chưa xác nhận đây là bản thử với hồ sơ minh họa
    fireEvent.click(screen.getByRole('button', { name: 'Gửi yêu cầu' }));
    expect(expertsService.submitConsultation).not.toHaveBeenCalled();
    fireEvent.click(screen.getByLabelText(/chỉ nhập thông tin giả định/));
    fireEvent.click(screen.getByLabelText(/Cho phép đối tác xem câu trả lời/));
    fireEvent.click(screen.getByRole('button', { name: 'Gửi yêu cầu' }));

    await waitFor(() =>
      expect(expertsService.submitConsultation).toHaveBeenCalledWith(
        expect.objectContaining({
          assessmentId: 'case-1',
          serviceNeeded: 'Kiểm tra và giải trình chênh lệch số liệu thuế',
          shareDataConsent: true,
          sampleAcknowledged: true,
        }),
      ),
    );
    expect(await screen.findByRole('status')).toHaveTextContent('đã nhận yêu cầu tư vấn');
  });
});
