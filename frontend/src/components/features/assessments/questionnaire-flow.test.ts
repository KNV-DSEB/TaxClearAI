import { describe, expect, it } from 'vitest';

import type { Answers, Question } from '@/types/api.types';

import {
  answerProblem,
  isAnswered,
  resetHiddenAnswers,
  visibleQuestions,
} from './questionnaire-flow';

const question = (
  id: string,
  extra: Partial<Question> = {},
  showIf?: Record<string, string[]>,
): Question => ({
  id,
  label: id,
  kind: 'choice',
  required: true,
  options: [],
  showIf,
  ...extra,
});

const questions = [
  question('businessType'),
  question('hhProvince', { kind: 'text' }, { businessType: ['household'] }),
  question('dnType', {}, { businessType: ['company'] }),
  question('lastRevenue', { kind: 'text', required: false }, { hasRevenue: ['yes'] }),
];

describe('Luồng câu hỏi rẽ nhánh', () => {
  it('chưa trả lời loại hình thì chỉ hiện câu chung', () => {
    expect(visibleQuestions(questions, {}).map((item) => item.id)).toEqual(['businessType']);
  });

  it('doanh nghiệp không được hỏi câu của hộ kinh doanh', () => {
    const answers: Answers = { businessType: 'company' };
    expect(visibleQuestions(questions, answers).map((item) => item.id)).toEqual([
      'businessType',
      'dnType',
    ]);
  });

  it('hộ kinh doanh không được hỏi câu của doanh nghiệp', () => {
    const answers: Answers = { businessType: 'household' };
    expect(visibleQuestions(questions, answers).map((item) => item.id)).toEqual([
      'businessType',
      'hhProvince',
    ]);
  });

  it('câu bổ sung chỉ hiện sau khi chọn đúng đáp án kích hoạt', () => {
    const answers: Answers = { businessType: 'company', hasRevenue: 'yes' };
    expect(visibleQuestions(questions, answers).map((item) => item.id)).toContain('lastRevenue');
    expect(
      visibleQuestions(questions, { businessType: 'company', hasRevenue: 'no' }).map(
        (item) => item.id,
      ),
    ).not.toContain('lastRevenue');
  });

  it('đổi loại hình thì đáp án của câu vừa bị ẩn bị xóa', () => {
    const answered: Answers = { businessType: 'company', hhProvince: 'Hà Nội', dnType: 'jsc' };
    const reset = resetHiddenAnswers(answered, questions);
    expect(reset.hhProvince).toBeNull();
    expect(reset.dnType).toBe('jsc');
  });
});

describe('Kiểm tra đáp án từng câu', () => {
  it('câu bắt buộc chưa trả lời thì chặn đi tiếp', () => {
    expect(answerProblem(question('a'), null)).toMatch(/trả lời câu này/);
    expect(answerProblem(question('a'), undefined)).toMatch(/trả lời câu này/);
  });

  it('câu không bắt buộc được bỏ trống', () => {
    expect(answerProblem(question('a', { required: false, kind: 'text' }), null)).toBe('');
    expect(answerProblem(question('a', { required: false, kind: 'number' }), '')).toBe('');
  });

  it.each(['Liên hệ 0901 234 567', 'khach@example.com', 'mã số thuế 0123456789'])(
    'ô tự điền không nhận thông tin nhận diện: %s',
    (text) => {
      expect(answerProblem(question('a', { kind: 'text' }), text)).toMatch(/không nhập email/);
    },
  );

  it('ô tự điền nhận chữ và ngày tháng thông thường', () => {
    expect(answerProblem(question('a', { kind: 'text' }), 'tháng 3/2024')).toBe('');
    expect(answerProblem(question('a', { kind: 'text' }), 'Đà Nẵng')).toBe('');
  });

  it('năm phải nằm trong khoảng hợp lệ', () => {
    const year = question('y', { kind: 'year', required: false });
    expect(answerProblem(year, 1800)).toMatch(/1900/);
    expect(answerProblem(year, new Date().getFullYear() + 1)).toMatch(/1900/);
    expect(answerProblem(year, 2015)).toBe('');
  });

  it('số tiền không được âm', () => {
    expect(answerProblem(question('m', { kind: 'number', required: false }), -5)).toMatch(
      /không âm/,
    );
    expect(answerProblem(question('m', { kind: 'number', required: false }), 1500000)).toBe('');
  });

  it('nhận biết giá trị đã trả lời, kể cả số 0', () => {
    expect(isAnswered(0)).toBe(true);
    expect(isAnswered('')).toBe(false);
    expect(isAnswered(null)).toBe(false);
  });
});
