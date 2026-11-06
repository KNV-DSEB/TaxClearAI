import { beforeEach, describe, expect, it } from 'vitest';

import { clearPlanPrompt, markPlanPrompt, peekPlanPrompt } from './plan-prompt';

describe('Gợi ý gói sau khảo sát', () => {
  beforeEach(() => sessionStorage.clear());

  it('hiện cho hồ sơ vừa tạo và tắt sau khi đã xóa dấu', () => {
    markPlanPrompt('case-1');
    expect(peekPlanPrompt('case-1')).toBe(true);
    clearPlanPrompt('case-1');
    expect(peekPlanPrompt('case-1')).toBe(false);
  });

  it('không hiện cho hồ sơ khác hoặc khi chưa đánh dấu', () => {
    expect(peekPlanPrompt('case-1')).toBe(false);
    markPlanPrompt('case-1');
    expect(peekPlanPrompt('case-2')).toBe(false);
  });

  it('xóa dấu của hồ sơ khác thì không ảnh hưởng hồ sơ đang chờ', () => {
    markPlanPrompt('case-1');
    clearPlanPrompt('case-2');
    expect(peekPlanPrompt('case-1')).toBe(true);
  });
});
