import { forwardRef, InputHTMLAttributes, ReactNode } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

import { cn } from '@/utils/cn';

const inputVariants = cva(
  'flex w-full rounded-md border bg-background text-sm text-foreground placeholder:text-muted-foreground transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
  {
    variants: {
      status: {
        default: 'border-input focus-visible:ring-ring',
        error: 'border-destructive focus-visible:ring-destructive',
        warning: 'border-yellow-500 focus-visible:ring-yellow-500',
      },
      size: {
        sm: 'h-8 px-2.5 text-sm',
        md: 'h-10 px-3 text-sm',
        lg: 'h-12 px-4 text-base',
      },
    },
    defaultVariants: {
      status: 'default',
      size: 'md',
    },
  }
);

export type InputProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'size' | 'prefix'> &
  VariantProps<typeof inputVariants> & {
    prefix?: ReactNode;
    suffix?: ReactNode;
  };

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics".
export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ status, size, prefix, suffix, className, disabled, ...props }, ref) => {
    if (!prefix && !suffix) {
      return <input ref={ref} disabled={disabled} className={cn(inputVariants({ status, size }), className)} {...props} />;
    }

    return (
      <div
        className={cn(
          inputVariants({ status, size }),
          'flex items-center gap-2 px-3',
          disabled && 'cursor-not-allowed opacity-50',
          className
        )}
      >
        {prefix && <span className="flex items-center text-muted-foreground">{prefix}</span>}
        <input
          ref={ref}
          disabled={disabled}
          className="w-full border-none bg-transparent p-0 text-sm text-foreground outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed"
          {...props}
        />
        {suffix && <span className="flex items-center text-muted-foreground">{suffix}</span>}
      </div>
    );
  }
);

Input.displayName = 'Input';
