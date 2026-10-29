import { ReactNode } from 'react';
import { create } from 'zustand';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export type NotificationConfig = {
  id: string;
  type: NotificationType;
  message: ReactNode;
  description?: ReactNode;
  duration?: number;
};

type NotificationStoreState = {
  notifications: NotificationConfig[];
  open: (config: Omit<NotificationConfig, 'id'>) => string;
  close: (id: string) => void;
};

// Backs notification's imperative API (notification.success/error/warning/info)
// — a queue any code can push into, rendered once by
// <NotificationContainer/> mounted in App.tsx.
export const useNotificationStore = create<NotificationStoreState>((set) => ({
  notifications: [],
  open: (config) => {
    const id = crypto.randomUUID();
    set((state) => ({ notifications: [...state.notifications, { ...config, id }] }));
    return id;
  },
  close: (id) =>
    set((state) => ({ notifications: state.notifications.filter((notification) => notification.id !== id) })),
}));
