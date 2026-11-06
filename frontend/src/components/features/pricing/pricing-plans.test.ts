import { describe, expect, it } from 'vitest';

import { EXPERT_FEE_EXAMPLE, FAQ, PLANS } from './pricing-plans';

describe('Bảng giá dự kiến', () => {
  it('chỉ gói miễn phí đang mở, hai gói trả phí ghi rõ chưa thu phí', () => {
    expect(PLANS.filter((plan) => plan.available).map((plan) => plan.id)).toEqual(['free']);
    for (const plan of PLANS.filter((item) => !item.available)) {
      expect(plan.statusLabel).toMatch(/chưa thu phí/);
    }
  });

  it('giữ đúng mức giá trong đề án: 250.000 đ mỗi hồ sơ và phí nền tảng 15%', () => {
    const [free, support, expert] = PLANS;
    expect(free.price).toBe('Miễn phí');
    expect(support.price).toBe('250.000 đ');
    expect(expert.price).toBe('Phí nền tảng 15%');
  });

  it('ví dụ phí nền tảng bằng 15% phí dịch vụ', () => {
    const toNumber = (text: string) => Number(text.replace(/\D/g, ''));
    expect(toNumber(EXPERT_FEE_EXAMPLE.platformFee)).toBe(
      toNumber(EXPERT_FEE_EXAMPLE.serviceFee) * 0.15,
    );
  });

  it('tính năng chưa có trong bản thử được gắn nhãn dự kiến', () => {
    const planned = PLANS.flatMap((plan) => plan.features).filter((feature) => feature.planned);
    expect(planned.length).toBeGreaterThan(0);
  });

  it('câu hỏi thường gặp nói rõ chưa phải trả tiền', () => {
    const first = FAQ[0];
    expect(first.answer).toMatch(/chưa thu/);
  });
});
