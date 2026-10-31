import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { ApiError } from '@/services/api.client';
import { assessmentsService } from '@/services/assessments.service';
import type { AssessmentListItem } from '@/types/api.types';

import { AssessmentList } from './AssessmentList';

const navigation = vi.hoisted(() => ({ replace: vi.fn() }));
vi.mock('next/navigation', () => ({ useRouter: () => navigation }));
vi.mock('@/services/assessments.service', () => ({
  assessmentsService: { list: vi.fn(), remove: vi.fn() },
}));

beforeEach(() => vi.resetAllMocks());

function item(changes: Partial<AssessmentListItem> = {}): AssessmentListItem {
  return {
    id: '11111111-1111-4111-8111-111111111111',
    scope: 'b2',
    counts: { available: 3, missing: 2, needsVerification: 14 },
    createdAt: '2026-10-30T08:00:00Z',
    updatedAt: '2026-10-31T08:00:00Z',
    expiresAt: '2026-11-06T08:00:00Z',
    expired: false,
    ...changes,
  };
}

function page(items: AssessmentListItem[], total = items.length, pageNumber = 1) {
  return { items, page: pageNumber, pageSize: 20, total };
}

describe('Hồ sơ của tôi', () => {
  it('liệt kê hồ sơ với số mục theo trạng thái và đường dẫn mở lại', async () => {
    vi.mocked(assessmentsService.list).mockResolvedValue(page([item()]));
    render(<AssessmentList />);
    expect(await screen.findByText('3 đã có · 2 còn thiếu · 14 cần xác minh')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Mở hồ sơ/ })).toHaveAttribute(
      'href',
      '/ho-so/11111111-1111-4111-8111-111111111111',
    );
  });

  it('hồ sơ hết hạn không mở được nhưng vẫn xóa được', async () => {
    vi.mocked(assessmentsService.list)
      .mockResolvedValueOnce(page([item({ expired: true })]))
      .mockResolvedValueOnce(page([]));
    vi.mocked(assessmentsService.remove).mockResolvedValue();
    render(<AssessmentList />);
    expect(await screen.findByText(/Đã hết hạn truy cập/)).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /Mở hồ sơ/ })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Xóa' }));
    fireEvent.click(screen.getByRole('button', { name: 'Xác nhận xóa hồ sơ' }));
    await waitFor(() =>
      expect(assessmentsService.remove).toHaveBeenCalledWith(
        '11111111-1111-4111-8111-111111111111',
      ),
    );
    expect(await screen.findByText('Chưa có hồ sơ nào được lưu.')).toBeInTheDocument();
  });

  it('chuyển sang đăng nhập và quay lại danh sách khi phiên hết hạn', async () => {
    vi.mocked(assessmentsService.list).mockRejectedValue(new ApiError(401, 'Phiên đã hết hạn.'));
    render(<AssessmentList />);
    await waitFor(() =>
      expect(navigation.replace).toHaveBeenCalledWith('/dang-nhap?returnTo=%2Fho-so'),
    );
  });

  it('báo lỗi khi xóa thất bại và giữ hồ sơ trong danh sách', async () => {
    vi.mocked(assessmentsService.list).mockResolvedValue(page([item()]));
    vi.mocked(assessmentsService.remove).mockRejectedValue(new Error('Chưa xóa được.'));
    render(<AssessmentList />);
    fireEvent.click(await screen.findByRole('button', { name: 'Xóa' }));
    fireEvent.click(screen.getByRole('button', { name: 'Xác nhận xóa hồ sơ' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Chưa xóa được.');
    expect(screen.getByText('3 đã có · 2 còn thiếu · 14 cần xác minh')).toBeInTheDocument();
  });

  it('phân trang khi có nhiều hơn một trang hồ sơ', async () => {
    vi.mocked(assessmentsService.list)
      .mockResolvedValueOnce(page([item()], 21))
      .mockResolvedValueOnce(page([item({ id: 'second' })], 21, 2));
    render(<AssessmentList />);
    expect(await screen.findByText('Trang 1/2')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Trang sau' }));
    expect(await screen.findByText('Trang 2/2')).toBeInTheDocument();
    expect(assessmentsService.list).toHaveBeenLastCalledWith(2, expect.any(AbortSignal));
  });
});
