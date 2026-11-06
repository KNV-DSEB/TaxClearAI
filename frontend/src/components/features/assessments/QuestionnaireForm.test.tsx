import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { ApiError } from '@/services/api.client';
import { assessmentsService } from '@/services/assessments.service';
import type { Assessment, Questionnaire } from '@/types/api.types';

import { QuestionnaireForm } from './QuestionnaireForm';

const navigation = vi.hoisted(() => ({ replace: vi.fn(), push: vi.fn() }));
vi.mock('next/navigation', () => ({ useRouter: () => navigation }));
vi.mock('@/services/assessments.service', () => ({
  assessmentsService: { questionnaire: vi.fn(), create: vi.fn() },
}));

const questionnaire: Questionnaire = {
  id: 'b2',
  version: 'groups-draft-3',
  contentStatus: 'draft',
  questions: [
    {
      id: 'businessType',
      label: 'Loại hình?',
      kind: 'choice',
      required: true,
      options: [
        { value: 'company', label: 'Doanh nghiệp' },
        { value: 'household', label: 'Hộ kinh doanh' },
      ],
    },
    {
      id: 'hasRevenue',
      label: 'Có doanh thu không?',
      kind: 'choice',
      required: true,
      options: [
        { value: 'yes', label: 'Có phát sinh doanh thu' },
        { value: 'no', label: 'Không phát sinh doanh thu' },
      ],
    },
    {
      id: 'lastRevenue',
      label: 'Doanh thu gần nhất khi nào?',
      kind: 'text',
      required: false,
      options: [],
      showIf: { hasRevenue: ['yes'] },
      help: 'Ví dụ: tháng 3/2024.',
    },
    {
      id: 'hhProvince',
      label: 'Hộ đăng ký ở đâu?',
      kind: 'text',
      required: true,
      options: [],
      showIf: { businessType: ['household'] },
    },
    {
      id: 'hhRevenueEstimate',
      label: 'Doanh thu ước tính?',
      kind: 'number',
      required: false,
      options: [],
      unit: 'đồng',
      showIf: { businessType: ['household'] },
    },
    { id: 'establishedYear', label: 'Năm thành lập?', kind: 'year', required: false, options: [] },
  ],
};

beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(assessmentsService.questionnaire).mockResolvedValue(questionnaire);
});

const NEXT = { name: 'Câu tiếp theo' };
const SAVE = { name: 'Lưu và xem hồ sơ' };

async function start(): Promise<void> {
  fireEvent.click(await screen.findByRole('button', { name: /Bắt đầu khảo sát/ }));
  await screen.findByRole('heading', { level: 2, name: 'Loại hình?' });
}

function pick(label: string): void {
  fireEvent.click(screen.getByLabelText(label));
  fireEvent.click(screen.getByRole('button', NEXT));
}

/** Hộ kinh doanh, không phát sinh doanh thu, tỉnh Đà Nẵng, bỏ trống hai câu không bắt buộc. */
async function fillHousehold(): Promise<void> {
  await start();
  pick('Hộ kinh doanh');
  pick('Không phát sinh doanh thu');
  fireEvent.change(screen.getByLabelText('Câu trả lời của bạn'), { target: { value: 'Đà Nẵng' } });
  fireEvent.click(screen.getByRole('button', NEXT));
  fireEvent.click(screen.getByRole('button', NEXT));
}

describe('Khảo sát trước buổi làm việc', () => {
  it('mở màn chào không nêu số câu cố định vì số câu đổi theo lựa chọn', async () => {
    render(<QuestionnaireForm />);
    expect(
      await screen.findByRole('heading', { name: /khảo sát tình trạng doanh nghiệp/ }),
    ).toBeInTheDocument();
    expect(screen.getByText(/số câu thay đổi theo loại hình/)).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Loại hình?' })).not.toBeInTheDocument();
  });

  it('câu bắt buộc phải được trả lời trước khi đi tiếp', async () => {
    render(<QuestionnaireForm />);
    await start();
    expect(screen.getByRole('button', NEXT)).toBeDisabled();
    fireEvent.click(screen.getByLabelText('Doanh nghiệp'));
    expect(screen.getByRole('button', NEXT)).toBeEnabled();
  });

  it('doanh nghiệp không bị hỏi câu chỉ dành cho hộ kinh doanh', async () => {
    render(<QuestionnaireForm />);
    await start();
    pick('Doanh nghiệp');
    expect(screen.getByRole('heading', { level: 2, name: 'Có doanh thu không?' })).toBeVisible();
    expect(screen.queryByText('Hộ đăng ký ở đâu?')).not.toBeInTheDocument();
  });

  it('câu bổ sung chỉ hiện sau khi chọn đáp án kích hoạt', async () => {
    render(<QuestionnaireForm />);
    await start();
    pick('Doanh nghiệp');
    pick('Có phát sinh doanh thu');
    expect(
      screen.getByRole('heading', { level: 2, name: 'Doanh thu gần nhất khi nào?' }),
    ).toBeVisible();
    expect(screen.getByText('Ví dụ: tháng 3/2024.')).toBeInTheDocument();
  });

  it('ô tự điền có thể bỏ trống nếu không bắt buộc, ô bắt buộc thì không', async () => {
    render(<QuestionnaireForm />);
    await start();
    pick('Hộ kinh doanh');
    pick('Không phát sinh doanh thu');
    expect(screen.getByRole('button', NEXT)).toBeDisabled();
    fireEvent.change(screen.getByLabelText('Câu trả lời của bạn'), { target: { value: 'Huế' } });
    expect(screen.getByRole('button', NEXT)).toBeEnabled();
    fireEvent.click(screen.getByRole('button', NEXT));
    expect(screen.getByText('đồng')).toBeInTheDocument();
    expect(screen.getByRole('button', NEXT)).toBeEnabled();
  });

  it('chặn thông tin nhận diện trong ô tự điền và nói rõ lý do', async () => {
    render(<QuestionnaireForm />);
    await start();
    pick('Doanh nghiệp');
    pick('Có phát sinh doanh thu');
    fireEvent.change(screen.getByLabelText('Có thể bỏ trống nếu chưa biết'), {
      target: { value: 'gọi 0901 234 567' },
    });
    fireEvent.click(screen.getByRole('button', NEXT));
    expect(screen.getByRole('alert')).toHaveTextContent('không nhập email, số điện thoại');
    expect(
      screen.getByRole('heading', { level: 2, name: 'Doanh thu gần nhất khi nào?' }),
    ).toBeVisible();
  });

  it('giữ câu trả lời khi quay lại và chỉ lưu khi xác nhận cuối luồng', async () => {
    vi.mocked(assessmentsService.create).mockResolvedValue({ id: 'saved-case' } as Assessment);
    render(<QuestionnaireForm />);
    await fillHousehold();
    expect(assessmentsService.create).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Quay lại' }));
    fireEvent.click(screen.getByRole('button', NEXT));
    fireEvent.click(screen.getByRole('button', SAVE));
    await waitFor(() =>
      expect(assessmentsService.create).toHaveBeenCalledWith(
        'groups-draft-3',
        expect.objectContaining({
          businessType: 'household',
          hasRevenue: 'no',
          hhProvince: 'Đà Nẵng',
          lastRevenue: null,
        }),
      ),
    );
    expect(navigation.push).toHaveBeenCalledWith('/ho-so/saved-case');
  });

  it('đổi loại hình thì đáp án của loại hình kia bị xóa trước khi lưu', async () => {
    vi.mocked(assessmentsService.create).mockResolvedValue({ id: 'saved-case' } as Assessment);
    render(<QuestionnaireForm />);
    await fillHousehold();
    for (let back = 0; back < 4; back += 1) {
      fireEvent.click(screen.getByRole('button', { name: 'Quay lại' }));
    }
    fireEvent.click(screen.getByLabelText('Doanh nghiệp'));
    fireEvent.click(screen.getByRole('button', NEXT));
    fireEvent.click(screen.getByRole('button', NEXT));
    fireEvent.click(screen.getByRole('button', SAVE));
    await waitFor(() =>
      expect(assessmentsService.create).toHaveBeenCalledWith(
        'groups-draft-3',
        expect.objectContaining({ businessType: 'company', hhProvince: null }),
      ),
    );
  });

  it('giữ nội dung khi API không lưu được và cho phép thử lại', async () => {
    vi.mocked(assessmentsService.create).mockRejectedValue(new Error('Chưa lưu được khảo sát.'));
    render(<QuestionnaireForm />);
    await fillHousehold();
    fireEvent.click(screen.getByRole('button', SAVE));
    expect(await screen.findByRole('alert')).toHaveTextContent('Chưa lưu được khảo sát.');
    expect(screen.getByRole('button', SAVE)).toBeEnabled();
    expect(navigation.push).not.toHaveBeenCalled();
  });

  it('yêu cầu đăng nhập khi không còn phiên hợp lệ', async () => {
    vi.mocked(assessmentsService.questionnaire).mockRejectedValue(
      new ApiError(401, 'Phiên đã hết hạn.'),
    );
    render(<QuestionnaireForm />);
    await waitFor(() => expect(navigation.replace).toHaveBeenCalledWith('/dang-nhap'));
  });
});
