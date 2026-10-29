'use client';

import { ReactElement, ReactNode } from 'react';
import * as TooltipPrimitive from '@radix-ui/react-tooltip';

import { cn } from '@/utils/cn';

type TooltipProps = {
  content: ReactNode;
  children: ReactElement;
  placement?: 'top' | 'bottom' | 'left' | 'right';
  disabled?: boolean;
  className?: string;
};

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics".
export function Tooltip({ content, children, placement = 'top', disabled = false, className }: TooltipProps) {
  if (disabled || !content) {
    return children;
  }

  return (
    <TooltipPrimitive.Provider delayDuration={200}>
      <TooltipPrimitive.Root>
        <TooltipPrimitive.Trigger asChild>{children}</TooltipPrimitive.Trigger>
        <TooltipPrimitive.Portal>
          <TooltipPrimitive.Content
            side={placement}
            sideOffset={6}
            className={cn(
              'z-50 overflow-hidden rounded-md bg-foreground px-3 py-1.5 text-xs text-background',
              'animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95',
              className
            )}
          >
            {content}
            <TooltipPrimitive.Arrow className="fill-foreground" />
          </TooltipPrimitive.Content>
        </TooltipPrimitive.Portal>
      </TooltipPrimitive.Root>
    </TooltipPrimitive.Provider>
  );
}
