'use client';

import { ReactElement, ReactNode } from 'react';
import * as DropdownMenuPrimitive from '@radix-ui/react-dropdown-menu';
import { ChevronRight } from 'lucide-react';

import { cn } from '@/utils/cn';

export type DropdownMenuItem =
  | {
      type: 'divider';
      key: string;
    }
  | {
      type?: 'item';
      key: string;
      label: ReactNode;
      icon?: ReactNode;
      disabled?: boolean;
      danger?: boolean;
      onClick?: () => void;
      children?: DropdownMenuItem[];
    };

type DropdownProps = {
  menu: { items: DropdownMenuItem[] };
  children: ReactElement;
  placement?: 'bottom-start' | 'bottom-end' | 'top-start' | 'top-end';
  disabled?: boolean;
};

const [side, align] = ['bottom', 'start'] as const;

function placementToSideAlign(placement: DropdownProps['placement']) {
  switch (placement) {
    case 'bottom-end':
      return { side: 'bottom' as const, align: 'end' as const };
    case 'top-start':
      return { side: 'top' as const, align: 'start' as const };
    case 'top-end':
      return { side: 'top' as const, align: 'end' as const };
    case 'bottom-start':
    default:
      return { side, align };
  }
}

function renderItems(items: DropdownMenuItem[]) {
  return items.map((item) => {
    if (item.type === 'divider') {
      return <DropdownMenuPrimitive.Separator key={item.key} className="my-1 h-px bg-border" />;
    }

    if (item.children && item.children.length > 0) {
      return (
        <DropdownMenuPrimitive.Sub key={item.key}>
          <DropdownMenuPrimitive.SubTrigger
            disabled={item.disabled}
            className={cn(
              'flex cursor-pointer select-none items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none',
              'focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
              item.danger && 'text-destructive focus:text-destructive'
            )}
          >
            {item.icon}
            <span className="flex-1">{item.label}</span>
            <ChevronRight className="h-4 w-4" aria-hidden />
          </DropdownMenuPrimitive.SubTrigger>
          <DropdownMenuPrimitive.Portal>
            <DropdownMenuPrimitive.SubContent
              className="z-50 min-w-[8rem] overflow-hidden rounded-md border border-border bg-popover p-1 text-popover-foreground shadow-md"
            >
              {renderItems(item.children)}
            </DropdownMenuPrimitive.SubContent>
          </DropdownMenuPrimitive.Portal>
        </DropdownMenuPrimitive.Sub>
      );
    }

    return (
      <DropdownMenuPrimitive.Item
        key={item.key}
        disabled={item.disabled}
        onSelect={() => item.onClick?.()}
        className={cn(
          'flex cursor-pointer select-none items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none',
          'focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
          item.danger && 'text-destructive focus:text-destructive'
        )}
      >
        {item.icon}
        <span>{item.label}</span>
      </DropdownMenuPrimitive.Item>
    );
  });
}

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics".
export function Dropdown({ menu, children, placement = 'bottom-start', disabled = false }: DropdownProps) {
  const { side: contentSide, align: contentAlign } = placementToSideAlign(placement);

  return (
    <DropdownMenuPrimitive.Root>
      <DropdownMenuPrimitive.Trigger asChild disabled={disabled}>
        {children}
      </DropdownMenuPrimitive.Trigger>
      <DropdownMenuPrimitive.Portal>
        <DropdownMenuPrimitive.Content
          side={contentSide}
          align={contentAlign}
          sideOffset={6}
          className={cn(
            'z-50 min-w-[8rem] overflow-hidden rounded-md border border-border bg-popover p-1 text-popover-foreground shadow-md',
            'animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95'
          )}
        >
          {renderItems(menu.items)}
        </DropdownMenuPrimitive.Content>
      </DropdownMenuPrimitive.Portal>
    </DropdownMenuPrimitive.Root>
  );
}
