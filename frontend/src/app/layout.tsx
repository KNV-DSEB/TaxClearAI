import type { Metadata } from 'next';

import { ModalContainer } from '../components/common/Modal';
import { NotificationContainer } from '../components/common/Notification';

import './globals.css';

export const metadata: Metadata = {
  title: 'Tax Clear AI — Chuẩn bị hồ sơ giải thể',
  description:
    'Ghi nhận tình trạng doanh nghiệp, sắp xếp checklist và chuẩn bị khảo sát với chuyên viên.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
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
