import { describe, expect, it } from 'vitest';

import type { Answers, Question } from '@/types/api.types';

import { resetHiddenAnswers, visibleQuestions } from './questionnaire-flow';

const base = {
  businessType: 'company',
  registrationStatus: 'unknown',
  establishedYear: null,
} as unknown as Answers;

const question = (id: keyof Answers, showIf?: Record<string, string[]>): Question => ({
  id,
  label: String(id),
  kind: 'choice',
  required: true,
  options: [],
  showIf,
});

const questions = [
  question('businessType'),
  question('registrationStatus', { businessType: ['household'] }),
  question('establishedYear', { businessType: ['company', 'unknown'] }),
];

describe('Luồng câu hỏi rẽ nhánh', () => {
  it('doanh nghiệp không được hỏi câu của hộ kinh doanh', () => {
    expect(visibleQuestions(questions, base).map((item) => item.id)).toEqual([
      'businessType',
      'establishedYear',
    ]);
  });

  it('hộ kinh doanh không được hỏi câu của doanh nghiệp', () => {
    const household = { ...base, businessType: 'household' } as Answers;
    expect(visibleQuestions(questions, household).map((item) => item.id)).toEqual([
      'businessType',
      'registrationStatus',
    ]);
  });

  it('câu không có điều kiện luôn được hỏi', () => {
    expect(visibleQuestions([question('businessType')], base)).toHaveLength(1);
  });

  it('đổi loại hình thì đáp án của câu vừa bị ẩn quay về mặc định', () => {
    const defaults = { ...base, registrationStatus: 'unknown' } as Answers;
    const answered = { ...base, businessType: 'company', registrationStatus: 'yes' } as Answers;
    expect(resetHiddenAnswers(answered, questions, defaults).registrationStatus).toBe('unknown');
  });

  it('giữ nguyên đáp án của câu vẫn đang được hỏi', () => {
    const answered = { ...base, establishedYear: 2015 } as unknown as Answers;
    expect(resetHiddenAnswers(answered, questions, base).establishedYear).toBe(2015);
  });
});
