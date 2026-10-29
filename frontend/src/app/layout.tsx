import type { Metadata } from 'next';

import { ModalContainer } from '../components/common/Modal';
import { NotificationContainer } from '../components/common/Notification';

import './globals.css';

export const metadata: Metadata = {
  title: '[PROJECT_NAME]',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
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
