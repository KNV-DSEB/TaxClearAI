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
  version: 'b2-draft-1',
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
      id: 'revenueStatus',
      label: 'Đã có doanh thu?',
      kind: 'choice',
      required: true,
      options: [
        { value: 'yes', label: 'Có' },
        { value: 'unknown', label: 'Chưa biết' },
      ],
    },
    { id: 'establishedYear', label: 'Năm thành lập?', kind: 'year', required: true, options: [] },
  ],
};

beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(assessmentsService.questionnaire).mockResolvedValue(questionnaire);
});

async function fillSurvey(): Promise<void> {
  fireEvent.click(await screen.findByRole('button', { name: /Bắt đầu khảo sát/ }));
  await screen.findByRole('heading', { level: 2, name: 'Loại hình?' });
  fireEvent.click(screen.getByLabelText('Hộ kinh doanh'));
  fireEvent.click(screen.getByRole('button', { name: 'Câu tiếp theo' }));
  fireEvent.click(screen.getByLabelText('Có'));
  fireEvent.click(screen.getByRole('button', { name: 'Câu tiếp theo' }));
}

describe('Khảo sát trước buổi làm việc', () => {
  it('mở màn chào với số câu thật trước khi vào câu hỏi', async () => {
    render(<QuestionnaireForm />);
    expect(
      await screen.findByRole('heading', { name: /khảo sát tình trạng doanh nghiệp/ }),
    ).toBeInTheDocument();
    expect(screen.getByText(/Bạn sẽ trả lời 3 câu hỏi ngắn/)).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Loại hình?' })).not.toBeInTheDocument();
  });

  it('giữ người dùng ở câu cần sửa khi năm doanh thu trước năm thành lập', async () => {
    vi.mocked(assessmentsService.questionnaire).mockResolvedValue({
      ...questionnaire,
      questions: [
        ...questionnaire.questions,
        {
          id: 'revenueStartedYear',
          label: 'Năm bắt đầu doanh thu?',
          kind: 'year',
          required: true,
          options: [],
        },
      ],
    });
    render(<QuestionnaireForm />);
    await fillSurvey();
    fireEvent.change(screen.getByLabelText('Năm (để trống nếu chưa biết hoặc không áp dụng)'), {
      target: { value: '2018' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Câu tiếp theo' }));
    fireEvent.change(screen.getByLabelText('Năm (để trống nếu chưa biết hoặc không áp dụng)'), {
      target: { value: '2010' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Lưu và xem hồ sơ' }));
    expect(screen.getByRole('alert')).toHaveTextContent(
      'Năm phát sinh doanh thu không được trước năm thành lập.',
    );
    expect(assessmentsService.create).not.toHaveBeenCalled();
  });

  it('giữ câu trả lời khi quay lại và chỉ lưu khi xác nhận cuối luồng', async () => {
    vi.mocked(assessmentsService.create).mockResolvedValue({ id: 'saved-case' } as Assessment);
    render(<QuestionnaireForm />);
    await fillSurvey();
    expect(assessmentsService.create).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Quay lại' }));
    expect(screen.getByLabelText('Có')).toBeChecked();
    fireEvent.click(screen.getByRole('button', { name: 'Câu tiếp theo' }));
    fireEvent.click(screen.getByRole('button', { name: 'Lưu và xem hồ sơ' }));
    await waitFor(() =>
      expect(assessmentsService.create).toHaveBeenCalledWith(
        'b2-draft-1',
        expect.objectContaining({
          businessType: 'household',
          revenueStatus: 'yes',
          establishedYear: null,
        }),
      ),
    );
    expect(navigation.push).toHaveBeenCalledWith('/ho-so/saved-case');
  });

  it('giữ nội dung khi API không lưu được và cho phép thử lại', async () => {
    vi.mocked(assessmentsService.create).mockRejectedValue(new Error('Chưa lưu được khảo sát.'));
    render(<QuestionnaireForm />);
    await fillSurvey();
    fireEvent.click(screen.getByRole('button', { name: 'Lưu và xem hồ sơ' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Chưa lưu được khảo sát.');
    expect(screen.getByRole('button', { name: 'Lưu và xem hồ sơ' })).toBeEnabled();
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
