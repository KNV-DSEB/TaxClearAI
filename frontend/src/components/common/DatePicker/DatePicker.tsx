'use client';

import { useState } from 'react';
import { format as formatDate } from 'date-fns';
import { CalendarIcon, ChevronLeft, ChevronRight } from 'lucide-react';
import { DayPicker } from 'react-day-picker';

import { Popover } from '@/components/common/Popover';
import { cn } from '@/utils/cn';

type DatePickerProps = {
  value?: Date;
  onChange?: (date: Date | undefined) => void;
  placeholder?: string;
  format?: string;
  disabledDate?: (date: Date) => boolean;
  disabled?: boolean;
  className?: string;
};

const navButtonClass =
  'inline-flex h-7 w-7 items-center justify-center rounded-md border border-input bg-background p-0 hover:bg-accent disabled:pointer-events-none disabled:opacity-50';

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics".
export function DatePicker({
  value,
  onChange,
  placeholder = 'Select date',
  format: displayFormat = 'dd/MM/yyyy',
  disabledDate,
  disabled = false,
  className,
}: DatePickerProps) {
  const [open, setOpen] = useState(false);

  return (
    <Popover
      open={open}
      onOpenChange={(next) => !disabled && setOpen(next)}
      placement="bottom"
      trigger={
        <button
          type="button"
          disabled={disabled}
          className={cn(
            'flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 text-sm text-foreground',
            'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
            className
          )}
        >
          <span className={cn(!value && 'text-muted-foreground')}>
            {value ? formatDate(value, displayFormat) : placeholder}
          </span>
          <CalendarIcon className="h-4 w-4 opacity-50" aria-hidden />
        </button>
      }
      content={
        <DayPicker
          mode="single"
          selected={value}
          onSelect={(date) => {
            onChange?.(date);
            setOpen(false);
          }}
          disabled={disabledDate}
          showOutsideDays
          components={{
            Chevron: ({ orientation }) =>
              orientation === 'left' ? (
                <ChevronLeft className="h-4 w-4" aria-hidden />
              ) : (
                <ChevronRight className="h-4 w-4" aria-hidden />
              ),
          }}
          classNames={{
            months: 'flex flex-col gap-4',
            month: 'space-y-3',
            month_caption: 'relative flex h-8 items-center justify-center',
            caption_label: 'text-sm font-medium text-foreground',
            nav: 'absolute inset-x-0 top-0 flex items-center justify-between',
            button_previous: navButtonClass,
            button_next: navButtonClass,
            month_grid: 'w-full border-collapse',
            weekdays: 'flex',
            weekday: 'w-9 text-center text-xs font-normal text-muted-foreground',
            week: 'mt-1 flex w-full',
            day: 'relative h-9 w-9 p-0 text-center text-sm',
            day_button:
              'inline-flex h-9 w-9 items-center justify-center rounded-md p-0 font-normal text-foreground hover:bg-accent aria-selected:opacity-100',
            selected: '[&>button]:bg-primary [&>button]:text-primary-foreground [&>button]:hover:bg-primary',
            today: 'text-primary [&>button]:font-semibold',
            outside: 'text-muted-foreground opacity-50',
            disabled: 'text-muted-foreground opacity-30',
            hidden: 'invisible',
          }}
        />
      }
    />
  );
}
