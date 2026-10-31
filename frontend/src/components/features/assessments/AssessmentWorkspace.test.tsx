import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { assessmentsService } from '@/services/assessments.service';

import { AssessmentWorkspace } from './AssessmentWorkspace';

const navigation = vi.hoisted(() => ({ replace: vi.fn() }));
vi.mock('next/navigation', () => ({ useRouter: () => navigation }));

vi.mock('@/services/assessments.service', () => ({
  assessmentsService: { updateItem: vi.fn(), remove: vi.fn(), list: vi.fn() },
}));

const assessment = {
  id: 'case-1',
  questionnaireVersion: 'b2-draft-1',
  contentStatus: 'draft' as const,
  answers: {},
  summary: {
    scope: 'b2' as const,
    knownFacts: ['Đã từng phát sinh doanh thu'],
    unknownFacts: ['Tình trạng kê khai chưa biết'],
    reviewReasons: [],
    notice: 'Nội dung mẫu, chờ cố vấn xác nhận.',
  },
  checklist: [
    {
      id: 'item-1',
      code: 'registration',
      label: 'Giấy đăng ký kinh doanh',
      status: 'needs_verification' as const,
      reviewStatus: 'draft' as const,
      note: null,
    },
  ],
  createdAt: '2026-10-30T00:00:00Z',
  updatedAt: '2026-10-30T00:00:00Z',
  expiresAt: '2026-11-06T00:00:00Z',
};

beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(assessmentsService.list).mockResolvedValue({
    items: [],
    page: 1,
    pageSize: 20,
    total: 3,
    statusCounts: { all: 3, inProgress: 2, ready: 1 },
  });
});

describe('Chuẩn bị hồ sơ khảo sát', () => {
  it('ẩn nhãn nội bộ cũ và vẫn hiển thị thông tin chưa biết', () => {
    render(<AssessmentWorkspace initial={assessment} />);
    expect(screen.queryByText(/cố vấn xác nhận/i)).not.toBeInTheDocument();
    expect(screen.getByText('Tình trạng kê khai chưa biết')).toBeInTheDocument();
  });

  it('hiển thị tên trung tính cho nhãn giấy tờ đã lưu từ phiên bản cũ', () => {
    render(
      <AssessmentWorkspace
        initial={{
          ...assessment,
          checklist: [
            {
              ...assessment.checklist[0],
              code: 'purchase_schedules',
              label: 'Bảng kê mua hàng theo mẫu cần cố vấn xác nhận',
            },
          ],
        }}
      />,
    );
    expect(screen.getByText('Bảng kê mua hàng theo kỳ áp dụng')).toBeInTheDocument();
    expect(screen.queryByText(/cố vấn xác nhận/i)).not.toBeInTheDocument();
  });

  it('chỉ báo lưu sau khi API xác nhận trạng thái giấy tờ', async () => {
    vi.mocked(assessmentsService.updateItem).mockResolvedValue({
      ...assessment.checklist[0],
      status: 'available',
    });
    render(<AssessmentWorkspace initial={assessment} />);
    fireEvent.change(screen.getByLabelText('Trạng thái: Giấy đăng ký kinh doanh'), {
      target: { value: 'available' },
    });
    await waitFor(() =>
      expect(assessmentsService.updateItem).toHaveBeenCalledWith('case-1', 'item-1', 'available'),
    );
    expect(await screen.findByText('Đã lưu trạng thái hồ sơ.')).toBeInTheDocument();
  });

  it('giữ trạng thái cũ khi lưu lỗi', async () => {
    vi.mocked(assessmentsService.updateItem).mockRejectedValue(new Error('Không lưu được.'));
    render(<AssessmentWorkspace initial={assessment} />);
    fireEvent.change(screen.getByLabelText('Trạng thái: Giấy đăng ký kinh doanh'), {
      target: { value: 'available' },
    });
    expect(await screen.findByRole('alert')).toHaveTextContent('Không lưu được.');
    expect(screen.getByLabelText('Trạng thái: Giấy đăng ký kinh doanh')).toHaveValue(
      'needs_verification',
    );
  });

  it('không xóa hồ sơ trước bước xác nhận và cho phép giữ lại', () => {
    render(<AssessmentWorkspace initial={assessment} />);
    fireEvent.click(screen.getByRole('button', { name: 'Xóa hồ sơ thử này' }));
    expect(assessmentsService.remove).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Giữ hồ sơ' }));
    expect(screen.queryByRole('button', { name: 'Xác nhận xóa hồ sơ' })).not.toBeInTheDocument();
  });

  it('chỉ rời hồ sơ khi server đã xác nhận xóa', async () => {
    vi.mocked(assessmentsService.remove).mockResolvedValue(undefined);
    render(<AssessmentWorkspace initial={assessment} />);
    fireEvent.click(screen.getByRole('button', { name: 'Xóa hồ sơ thử này' }));
    fireEvent.click(screen.getByRole('button', { name: 'Xác nhận xóa hồ sơ' }));
    await waitFor(() => expect(navigation.replace).toHaveBeenCalledWith('/ho-so'));
    expect(assessmentsService.remove).toHaveBeenCalledWith('case-1');
  });

  it('giữ trang và báo lỗi khi xóa thất bại', async () => {
    vi.mocked(assessmentsService.remove).mockRejectedValue(new Error('Chưa xóa được.'));
    render(<AssessmentWorkspace initial={assessment} />);
    fireEvent.click(screen.getByRole('button', { name: 'Xóa hồ sơ thử này' }));
    fireEvent.click(screen.getByRole('button', { name: 'Xác nhận xóa hồ sơ' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Chưa xóa được.');
    expect(navigation.replace).not.toHaveBeenCalled();
  });

  it('hiển thị tiến trình, số mục còn cần chuẩn bị và bộ đếm hồ sơ', async () => {
    render(<AssessmentWorkspace initial={assessment} />);
    expect(
      screen.getByRole('heading', { name: 'Hồ sơ: Giải thể doanh nghiệp' }),
    ).toBeInTheDocument();
    expect(screen.getByText('Đang thực hiện', { selector: '.badge' })).toBeInTheDocument();
    expect(screen.getByText(/1 mục cần chuẩn bị/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Tải bản tổng hợp/ })).toHaveAttribute(
      'href',
      '/ho-so/case-1/ban-in',
    );
    const steps = screen.getByRole('list', { name: 'Tiến trình hồ sơ' });
    expect(steps.querySelector('[aria-current="step"]')).toHaveTextContent('Chuẩn bị hồ sơ');
    expect(await screen.findByText('3')).toBeInTheDocument();
  });

  it('chuyển sang Đã đủ giấy tờ khi mọi mục là Đã có, không gọi là hoàn tất thủ tục', async () => {
    vi.mocked(assessmentsService.updateItem).mockResolvedValue({
      ...assessment.checklist[0],
      status: 'available',
    });
    render(<AssessmentWorkspace initial={assessment} />);
    fireEvent.change(screen.getByLabelText('Trạng thái: Giấy đăng ký kinh doanh'), {
      target: { value: 'available' },
    });
    expect(await screen.findByText('Đã đủ giấy tờ', { selector: '.badge' })).toBeInTheDocument();
    expect(screen.queryByText(/hoàn tất thủ tục/i)).not.toBeInTheDocument();
  });

  it('không tạo checklist sai phạm vi', () => {
    render(
      <AssessmentWorkspace
        initial={{
          ...assessment,
          checklist: [],
          summary: {
            ...assessment.summary,
            scope: 'out_of_scope',
          },
        }}
      />,
    );
    expect(screen.getByText('Cần xác nhận phạm vi trước.')).toBeInTheDocument();
    expect(screen.queryByRole('combobox')).not.toBeInTheDocument();
  });
});
