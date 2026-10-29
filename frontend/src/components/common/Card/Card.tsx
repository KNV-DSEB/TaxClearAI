import { HTMLAttributes, ReactNode } from 'react';

import { cn } from '@/utils/cn';

type CardProps = HTMLAttributes<HTMLDivElement> & {
  title?: ReactNode;
  extra?: ReactNode;
  bordered?: boolean;
  hoverable?: boolean;
  size?: 'default' | 'small';
  actions?: ReactNode[];
};

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics".
export function Card({
  title,
  extra,
  bordered = true,
  hoverable = false,
  size = 'default',
  actions,
  className,
  children,
  ...props
}: CardProps) {
  return (
    <div
      className={cn(
        'rounded-lg bg-card text-card-foreground',
        bordered && 'border border-border',
        hoverable && 'transition-shadow hover:shadow-md',
        className
      )}
      {...props}
    >
      {(title || extra) && (
        <div
          className={cn(
            'flex items-center justify-between border-b border-border',
            size === 'small' ? 'px-3 py-2' : 'px-4 py-3'
          )}
        >
          {title && <div className="font-medium text-foreground">{title}</div>}
          {extra && <div className="cursor-pointer text-muted-foreground hover:text-foreground">{extra}</div>}
        </div>
      )}
      <div className={size === 'small' ? 'p-3' : 'p-4'}>{children}</div>
      {actions && actions.length > 0 && (
        <ul className="flex divide-x divide-border border-t border-border">
          {actions.map((action, index) => (
             
            <li key={index} className="flex flex-1 cursor-pointer items-center justify-center py-2 text-muted-foreground hover:text-foreground">
              {action}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
