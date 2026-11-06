import type { Metadata, Viewport } from 'next';
import { Be_Vietnam_Pro } from 'next/font/google';

import { ModalContainer } from '../components/common/Modal';
import { NotificationContainer } from '../components/common/Notification';

import './globals.css';

const beVietnamPro = Be_Vietnam_Pro({
  subsets: ['latin', 'vietnamese'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-brand',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Tax Clear — Chuẩn bị hồ sơ giải thể',
  description:
    'Ghi nhận tình trạng doanh nghiệp, sắp xếp checklist và chuẩn bị khảo sát với chuyên viên.',
  applicationName: 'Tax Clear',
  openGraph: {
    title: 'Tax Clear — Giải thể gọn gàng. An tâm sang trang.',
    description: 'Trợ lý chuẩn bị hồ sơ giải thể cho doanh nghiệp. Bản thử nghiệm.',
    locale: 'vi_VN',
    type: 'website',
  },
};

export const viewport: Viewport = { themeColor: '#0f5a4c' };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" className={beVietnamPro.variable}>
      <body>
        {children}
        {/* Renders modal.confirm()/notification.success()/... calls made anywhere
           in the app — see components/common/Modal and Notification. */}
        <ModalContainer />
        <NotificationContainer />
      </body>
    </html>
  );
}
