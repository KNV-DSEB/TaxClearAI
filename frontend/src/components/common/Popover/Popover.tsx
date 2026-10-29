'use client';

import { ReactElement, ReactNode } from 'react';
import * as PopoverPrimitive from '@radix-ui/react-popover';

import { cn } from '@/utils/cn';

type PopoverProps = {
  trigger: ReactElement;
  content: ReactNode;
  open?: boolean;
  defaultOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
  placement?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
};

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics".
export function Popover({
  trigger,
  content,
  open,
  defaultOpen,
  onOpenChange,
  placement = 'bottom',
  className,
}: PopoverProps) {
  return (
    <PopoverPrimitive.Root open={open} defaultOpen={defaultOpen} onOpenChange={onOpenChange}>
      <PopoverPrimitive.Trigger asChild>{trigger}</PopoverPrimitive.Trigger>
      <PopoverPrimitive.Portal>
        <PopoverPrimitive.Content
          side={placement}
          sideOffset={6}
          className={cn(
            'z-50 w-72 rounded-md border border-border bg-popover p-4 text-popover-foreground shadow-md outline-none',
            'animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95',
            className
          )}
        >
          {content}
          <PopoverPrimitive.Arrow className="fill-popover" />
        </PopoverPrimitive.Content>
      </PopoverPrimitive.Portal>
    </PopoverPrimitive.Root>
  );
}
