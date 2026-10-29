'use client';

import { ChangeEvent, forwardRef, InputHTMLAttributes, ReactNode, useId } from 'react';
import { Check } from 'lucide-react';

import { cn } from '@/utils/cn';

export type CheckboxProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'value' | 'onChange' | 'size'> & {
  checked?: boolean;
  /** Alias for `checked` — lets Form.Item's generic `value`/`onChange` field spread work unmodified. */
  value?: boolean;
  onChange?: (event: ChangeEvent<HTMLInputElement>) => void;
  label?: ReactNode;
};

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics".
export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ checked, value, onChange, label, className, disabled, id, ...props }, ref) => {
    const autoId = useId();
    const inputId = id ?? autoId;
    const isChecked = checked ?? value ?? false;

    return (
      <label
        htmlFor={inputId}
        className={cn(
          'inline-flex items-center gap-2 text-sm text-foreground',
          disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
          className
        )}
      >
        <span className="relative flex h-4 w-4 shrink-0 items-center justify-center">
          <input
            ref={ref}
            id={inputId}
            type="checkbox"
            checked={isChecked}
            onChange={onChange}
            disabled={disabled}
            className={cn(
              'peer h-4 w-4 shrink-0 cursor-pointer appearance-none rounded-sm border border-input bg-background transition-colors',
              'checked:border-primary checked:bg-primary',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
              'disabled:cursor-not-allowed'
            )}
            {...props}
          />
          <Check
            className="pointer-events-none absolute h-3 w-3 text-primary-foreground opacity-0 peer-checked:opacity-100"
            aria-hidden
          />
        </span>
        {label && <span>{label}</span>}
      </label>
    );
  }
);

Checkbox.displayName = 'Checkbox';
