import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { ApiError } from '@/services/api.client';
import { assessmentsService } from '@/services/assessments.service';
import type { Assessment } from '@/types/api.types';

import { PrintSummary } from './PrintSummary';

const navigation = vi.hoisted(() => ({ replace: vi.fn() }));
vi.mock('next/navigation', () => ({ useRouter: () => navigation }));
vi.mock('@/services/assessments.service', () => ({ assessmentsService: { get: vi.fn() } }));

const assessment = {
  id: 'case-1',
  questionnaireVersion: 'b2-draft-1',
  contentStatus: 'draft',
  answers: {},
  summary: {
    scope: 'b2',
    knownFacts: ['Loại hình — Doanh nghiệp'],
    unknownFacts: ['Tình trạng kê khai'],
    reviewReasons: ['Tình trạng kê khai cần được chuyên viên xác minh.'],
    notice: 'Bản tổng hợp để trao đổi với chuyên viên.',
  },
  checklist: [
    {
      id: 'i1',
      code: 'registration',
      label: 'Giấy đăng ký kinh doanh',
      status: 'missing',
      reviewStatus: 'draft',
      note: null,
    },
  ],
  createdAt: '2026-10-30T00:00:00Z',
  updatedAt: '2026-10-31T03:24:00Z',
  expiresAt: '2099-01-01T00:00:00Z',
} as unknown as Assessment;

beforeEach(() => vi.resetAllMocks());

describe('Bản in tổng hợp', () => {
  it('liệt kê thông tin hồ sơ, điểm cần xác minh, checklist và mở hộp thoại in', async () => {
    vi.mocked(assessmentsService.get).mockResolvedValue(assessment);
    const print = vi.spyOn(window, 'print').mockImplementation(() => undefined);
    render(<PrintSummary id="case-1" />);
    expect(await screen.findByText('Bản tổng hợp đã sẵn sàng')).toBeInTheDocument();
    expect(screen.getByText('Giải thể doanh nghiệp')).toBeInTheDocument();
    expect(screen.getByRole('cell', { name: 'Còn thiếu' })).toBeInTheDocument();
    expect(screen.getByText(/không phải kết luận pháp lý/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /In bản tổng hợp/ }));
    expect(print).toHaveBeenCalled();
  });

  it('chuyển sang đăng nhập khi hết phiên', async () => {
    vi.mocked(assessmentsService.get).mockRejectedValue(new ApiError(401, 'Phiên đã hết hạn.'));
    render(<PrintSummary id="case-1" />);
    await waitFor(() =>
      expect(navigation.replace).toHaveBeenCalledWith('/dang-nhap?returnTo=%2Fho-so%2Fcase-1'),
    );
  });
});
