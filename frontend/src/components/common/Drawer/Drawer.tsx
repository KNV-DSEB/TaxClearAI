'use client';

import { ReactNode } from 'react';
import * as DialogPrimitive from '@radix-ui/react-dialog';
import { X } from 'lucide-react';

import { cn } from '@/utils/cn';

type DrawerProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title?: ReactNode;
  footer?: ReactNode | null;
  children?: ReactNode;
  closable?: boolean;
  width?: number | string;
  className?: string;
};

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics". Side panel that slides in from the right, sized for
// content wider/taller than what fits comfortably in a centered Modal (e.g.
// a file upload step followed by a multi-column preview table).
export function Drawer({
  open,
  onOpenChange,
  title,
  footer,
  children,
  closable = true,
  width = 640,
  className,
}: DrawerProps) {
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
            'fixed inset-y-0 right-0 z-50 flex h-full max-w-[95vw] flex-col border-l border-border bg-background p-6 shadow-lg',
            'data-[state=open]:animate-in data-[state=open]:slide-in-from-right data-[state=open]:duration-200 data-[state=open]:ease-out',
            'data-[state=closed]:animate-out data-[state=closed]:slide-out-to-right data-[state=closed]:duration-150 data-[state=closed]:ease-in',
            className
          )}
        >
          {title ? (
            <DialogPrimitive.Title className="mb-4 shrink-0 pr-6 text-lg font-semibold text-foreground">
              {title}
            </DialogPrimitive.Title>
          ) : (
            <DialogPrimitive.Title className="sr-only">Drawer</DialogPrimitive.Title>
          )}
          <div className="min-h-0 flex-1 overflow-y-auto text-sm text-foreground">{children}</div>
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
