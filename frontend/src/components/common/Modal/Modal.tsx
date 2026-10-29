'use client';

import { ReactNode } from 'react';
import * as DialogPrimitive from '@radix-ui/react-dialog';
import { X } from 'lucide-react';

import { cn } from '@/utils/cn';

import { type ModalConfig, useModalStore } from '@/store/modal.store';

type ModalProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title?: ReactNode;
  footer?: ReactNode | null;
  children?: ReactNode;
  closable?: boolean;
  width?: number | string;
  className?: string;
};

function ModalBase({
  open,
  onOpenChange,
  title,
  footer,
  children,
  closable = true,
  width = 480,
  className,
}: ModalProps) {
  return (
    <DialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay
          className={cn(
            'fixed inset-0 z-50 bg-black/50',
            'data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:duration-200 data-[state=open]:ease-out',
            'data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:duration-150 data-[state=closed]:ease-in'
          )}
        />
        <DialogPrimitive.Content
          style={{ width }}
          className={cn(
            'fixed left-1/2 top-1/2 z-50 flex max-h-[85vh] max-w-[90vw] -translate-x-1/2 -translate-y-1/2 flex-col rounded-lg border border-border bg-background p-6 shadow-lg',
            'data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95 data-[state=open]:slide-in-from-top-2 data-[state=open]:duration-200 data-[state=open]:ease-out',
            'data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[state=closed]:slide-out-to-top-2 data-[state=closed]:duration-150 data-[state=closed]:ease-in',
            className
          )}
        >
          {title ? (
            <DialogPrimitive.Title className="mb-4 shrink-0 pr-6 text-lg font-semibold text-foreground">
              {title}
            </DialogPrimitive.Title>
          ) : (
            <DialogPrimitive.Title className="sr-only">Dialog</DialogPrimitive.Title>
          )}
          {/* min-h-0 lets this shrink inside the flex column instead of forcing the dialog past the viewport — without it a tall form (e.g. AppFormModal) renders with its bottom fields unreachable, no scroll. */}
          <div className="min-h-0 overflow-y-auto text-sm text-foreground">{children}</div>
          {footer !== null && <div className="mt-6 flex shrink-0 justify-end gap-2">{footer}</div>}
          {closable && (
            <DialogPrimitive.Close
              aria-label="Close"
              className="absolute right-4 top-4 rounded-sm text-muted-foreground opacity-70 hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <X className="h-4 w-4" aria-hidden />
            </DialogPrimitive.Close>
          )}
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}

type StaticModalConfig = Omit<ModalConfig, 'id' | 'type'>;

function openModal(type: ModalConfig['type'], config: StaticModalConfig) {
  return useModalStore.getState().open({ showCancel: type === 'confirm', ...config, type });
}

function confirm(config: StaticModalConfig) {
  return openModal('confirm', config);
}
function info(config: StaticModalConfig) {
  return openModal('info', config);
}
function success(config: StaticModalConfig) {
  return openModal('success', config);
}
function error(config: StaticModalConfig) {
  return openModal('error', config);
}
function warning(config: StaticModalConfig) {
  return openModal('warning', config);
}

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics". Controlled usage: <Modal open onOpenChange>...
// Imperative usage: Modal.confirm({ title, content, onOk }) — see
// ModalContainer for how the queued config gets rendered.
export const Modal = Object.assign(ModalBase, { confirm, info, success, error, warning });
