'use client';

import { type ReactElement, useState } from 'react';
import * as ToastPrimitive from '@radix-ui/react-toast';
import { AlertTriangle, CheckCircle2, Info, X, XCircle } from 'lucide-react';

import { cn } from '@/utils/cn';
import { type NotificationConfig, type NotificationType, useNotificationStore } from '@/store/notification.store';

const DEFAULT_DURATION_MS = 4500;

const iconByType: Record<NotificationType, ReactElement> = {
  success: <CheckCircle2 className="h-5 w-5 shrink-0 text-green-500" aria-hidden />,
  error: <XCircle className="h-5 w-5 shrink-0 text-destructive" aria-hidden />,
  warning: <AlertTriangle className="h-5 w-5 shrink-0 text-yellow-500" aria-hidden />,
  info: <Info className="h-5 w-5 shrink-0 text-primary" aria-hidden />,
};

const barColorByType: Record<NotificationType, string> = {
  success: 'bg-green-500',
  error: 'bg-destructive',
  warning: 'bg-yellow-500',
  info: 'bg-primary',
};

type NotificationToastProps = {
  item: NotificationConfig;
  onClose: () => void;
};

// Split out so each toast owns its own "is the pointer hovering it" state —
// Radix's onPause/onResume already drives the real dismiss timer (built
// into the primitive, see NotificationContainer's module comment), this
// just mirrors that into the countdown bar's CSS animation so both stay in
// sync without re-implementing the timer itself.
function NotificationToast({ item, onClose }: NotificationToastProps) {
  const [paused, setPaused] = useState(false);
  const duration = item.duration ?? DEFAULT_DURATION_MS;

  return (
    <ToastPrimitive.Root
      duration={duration}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
      onPause={() => setPaused(true)}
      onResume={() => setPaused(false)}
      className={cn(
        'relative grid grid-cols-[auto_1fr_auto] items-start gap-3 overflow-hidden rounded-md border border-border bg-background p-4 shadow-lg',
        'data-[state=open]:animate-in data-[state=open]:slide-in-from-right-full data-[state=closed]:animate-out data-[state=closed]:fade-out-80'
      )}
    >
      {iconByType[item.type]}
      <div className="grid gap-1">
        <ToastPrimitive.Title className="text-sm font-medium text-foreground">{item.message}</ToastPrimitive.Title>
        {item.description && (
          <ToastPrimitive.Description className="text-sm text-muted-foreground">
            {item.description}
          </ToastPrimitive.Description>
        )}
      </div>
      <ToastPrimitive.Close aria-label="Close" className="text-muted-foreground hover:text-foreground">
        <X className="h-4 w-4" aria-hidden />
      </ToastPrimitive.Close>
      {/* Right edge recedes toward the fixed left edge — empty means time's
          up. No numbers by design (see conversation), purely visual. */}
      <div
        aria-hidden
        data-testid="notification-countdown-bar"
        className={cn('absolute inset-x-0 bottom-0 h-1 origin-left opacity-90', barColorByType[item.type])}
        style={{
          animationName: 'toast-countdown',
          animationDuration: `${duration}ms`,
          animationTimingFunction: 'linear',
          animationFillMode: 'forwards',
          animationPlayState: paused ? 'paused' : 'running',
        }}
      />
    </ToastPrimitive.Root>
  );
}

// Mount this once near the root of the app (see App.tsx) so
// notification.success()/error()/warning()/info() can be called from
// anywhere. Reusable UI ONLY — no business logic beyond wiring the store's
// queue to Radix's toast primitives. Auto-dismiss (`duration`), stacking
// newest-at-bottom (notifications array is appended to, viewport is
// flex-col) and pause-on-hover are Radix Toast's own built-in behavior —
// see @radix-ui/react-toast's internal pointermove/blur handling.
export function NotificationContainer() {
  const notifications = useNotificationStore((state) => state.notifications);
  const close = useNotificationStore((state) => state.close);

  return (
    <ToastPrimitive.Provider swipeDirection="right">
      {notifications.map((item) => (
        <NotificationToast key={item.id} item={item} onClose={() => close(item.id)} />
      ))}
      <ToastPrimitive.Viewport className="fixed right-0 top-0 z-[100] flex w-96 max-w-[100vw] flex-col gap-2 p-4" />
    </ToastPrimitive.Provider>
  );
}
