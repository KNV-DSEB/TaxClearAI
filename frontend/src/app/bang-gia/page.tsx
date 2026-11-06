import type { Metadata } from 'next';

import { AppShell } from '@/components/features/navigation/AppShell';
import { PricingOverview } from '@/components/features/pricing/PricingOverview';

export const metadata: Metadata = {
  title: 'Bảng giá — Tax Clear',
  description:
    'Bắt đầu miễn phí. Giá các gói hỗ trợ hồ sơ và kết nối chuyên gia là dự kiến, bản thử chưa thu phí.',
};

export default function PricingPage() {
  return (
    <AppShell active="pricing">
      <main id="main-content" className="page">
        <PricingOverview />
      </main>
    </AppShell>
  );
}
