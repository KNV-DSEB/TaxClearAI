import { forwardRef, TextareaHTMLAttributes } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

import { cn } from '@/utils/cn';

const textAreaVariants = cva(
  'flex w-full rounded-md border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
  {
    variants: {
      status: {
        default: 'border-input focus-visible:ring-ring',
        error: 'border-destructive focus-visible:ring-destructive',
        warning: 'border-yellow-500 focus-visible:ring-yellow-500',
      },
    },
    defaultVariants: {
      status: 'default',
    },
  }
);

type TextAreaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & VariantProps<typeof textAreaVariants>;

export const TextArea = forwardRef<HTMLTextAreaElement, TextAreaProps>(({ status, className, rows = 4, ...props }, ref) => (
  <textarea ref={ref} rows={rows} className={cn(textAreaVariants({ status }), className)} {...props} />
));

TextArea.displayName = 'Input.TextArea';
