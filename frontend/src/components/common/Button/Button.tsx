import { forwardRef, ButtonHTMLAttributes, ReactNode } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { Loader2 } from 'lucide-react';

import { cn } from '@/utils/cn';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      type: {
        primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
        default: 'border border-input bg-background text-foreground hover:bg-accent',
        dashed: 'border border-dashed border-input bg-background text-foreground hover:bg-accent',
        text: 'text-foreground hover:bg-accent',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      danger: {
        true: '',
        false: '',
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-sm',
        lg: 'h-12 px-6 text-base',
      },
    },
    compoundVariants: [
      { type: 'primary', danger: true, class: 'bg-destructive text-destructive-foreground hover:bg-destructive/90' },
      { type: 'default', danger: true, class: 'border-destructive text-destructive hover:bg-destructive/10' },
      { type: 'dashed', danger: true, class: 'border-destructive text-destructive hover:bg-destructive/10' },
      { type: 'text', danger: true, class: 'text-destructive hover:bg-destructive/10' },
      { type: 'link', danger: true, class: 'text-destructive' },
    ],
    defaultVariants: {
      type: 'default',
      danger: false,
      size: 'md',
    },
  }
);

type ButtonProps = Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'type'> &
  VariantProps<typeof buttonVariants> & {
    /** Native HTML button type attribute (mirrors antd's `htmlType`, since `type` here is the visual variant). */
    htmlType?: ButtonHTMLAttributes<HTMLButtonElement>['type'];
    loading?: boolean;
    icon?: ReactNode;
  };

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics". forwardRef is required so Radix primitives
// (Popover/Tooltip/DropdownMenu/Popconfirm) can use Button as an `asChild`
// trigger and measure its real DOM node for positioning.
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ type, danger, size, htmlType = 'button', loading = false, icon, disabled, className, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        type={htmlType}
        className={cn(buttonVariants({ type, danger, size }), className)}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> : icon}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
