'use client';

import { ReactNode, useMemo, useState } from 'react';
import * as SelectPrimitive from '@radix-ui/react-select';
import { Check, ChevronDown, X } from 'lucide-react';

import { cn } from '@/utils/cn';

export type SelectOption = {
  label: ReactNode;
  value: string;
  disabled?: boolean;
};

type SelectProps = {
  options: SelectOption[];
  value?: string;
  onChange?: (value: string | undefined) => void;
  placeholder?: string;
  allowClear?: boolean;
  showSearch?: boolean;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
};

const SELECT_TRIGGER_SIZE_CLASSES: Record<NonNullable<SelectProps['size']>, string> = {
  sm: 'h-8 pl-2.5 text-sm',
  md: 'h-10 pl-3 text-sm',
  lg: 'h-12 pl-4 text-base',
};

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics".
export function Select({
  options,
  value,
  onChange,
  placeholder = 'Select',
  allowClear = false,
  showSearch = false,
  disabled = false,
  size = 'md',
  className,
}: SelectProps) {
  const [search, setSearch] = useState('');

  const filteredOptions = useMemo(() => {
    if (!showSearch || !search.trim()) {
      return options;
    }
    const query = search.trim().toLowerCase();
    return options.filter((option) => String(option.label).toLowerCase().includes(query));
  }, [options, search, showSearch]);

  const showClear = allowClear && !!value;

  return (
    <SelectPrimitive.Root
      value={value ?? ''}
      onValueChange={(next) => onChange?.(next || undefined)}
      disabled={disabled}
    >
      <div className="relative">
        <SelectPrimitive.Trigger
          className={cn(
            'flex w-full items-center rounded-md border border-input bg-background text-foreground',
            'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
            '[&>span]:line-clamp-1',
            SELECT_TRIGGER_SIZE_CLASSES[size],
            showClear ? 'pr-14' : 'pr-8',
            className
          )}
        >
          <SelectPrimitive.Value placeholder={placeholder} />
        </SelectPrimitive.Trigger>
        <SelectPrimitive.Icon asChild>
          <ChevronDown
            className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground opacity-50"
            aria-hidden
          />
        </SelectPrimitive.Icon>
        {showClear && (
          <button
            type="button"
            aria-label="Clear selection"
            onPointerDown={(event) => event.stopPropagation()}
            onClick={(event) => {
              event.stopPropagation();
              onChange?.(undefined);
            }}
            className="absolute right-8 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            <X className="h-3.5 w-3.5" aria-hidden />
          </button>
        )}
      </div>
      <SelectPrimitive.Portal>
        <SelectPrimitive.Content
          className={cn(
            'z-50 max-h-96 w-[var(--radix-select-trigger-width)] min-w-[8rem] overflow-hidden rounded-md border border-border bg-popover text-popover-foreground shadow-md',
            'animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95'
          )}
          position="popper"
          sideOffset={4}
        >
          {showSearch && (
            <div className="border-b border-border p-2">
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                onKeyDown={(event) => event.stopPropagation()}
                placeholder="Search..."
                className="w-full rounded border border-input bg-background px-2 py-1 text-sm text-foreground outline-none"
              />
            </div>
          )}
          <SelectPrimitive.Viewport className="p-1">
            {filteredOptions.length === 0 ? (
              <div className="py-6 text-center text-sm text-muted-foreground">No data</div>
            ) : (
              filteredOptions.map((option) => (
                <SelectPrimitive.Item
                  key={option.value}
                  value={option.value}
                  disabled={option.disabled}
                  className={cn(
                    'relative flex cursor-pointer select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none',
                    'focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50'
                  )}
                >
                  <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
                    <SelectPrimitive.ItemIndicator>
                      <Check className="h-4 w-4" aria-hidden />
                    </SelectPrimitive.ItemIndicator>
                  </span>
                  <SelectPrimitive.ItemText>{option.label}</SelectPrimitive.ItemText>
                </SelectPrimitive.Item>
              ))
            )}
          </SelectPrimitive.Viewport>
        </SelectPrimitive.Content>
      </SelectPrimitive.Portal>
    </SelectPrimitive.Root>
  );
}
