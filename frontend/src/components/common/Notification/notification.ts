import { type NotificationConfig, type NotificationType, useNotificationStore } from '@/store/notification.store';

type StaticNotificationConfig = Omit<NotificationConfig, 'id' | 'type'>;

function openNotification(type: NotificationType, config: StaticNotificationConfig) {
  return useNotificationStore.getState().open({ ...config, type });
}

// Purely imperative, like antd's `notification` — call from anywhere
// (including outside a component). See NotificationContainer for how the
// queued config gets rendered.
export const notification = {
  open: (config: StaticNotificationConfig & { type?: NotificationType }) =>
    useNotificationStore.getState().open({ ...config, type: config.type ?? 'info' }),
  success: (config: StaticNotificationConfig) => openNotification('success', config),
  error: (config: StaticNotificationConfig) => openNotification('error', config),
  warning: (config: StaticNotificationConfig) => openNotification('warning', config),
  info: (config: StaticNotificationConfig) => openNotification('info', config),
  close: (id: string) => useNotificationStore.getState().close(id),
};
