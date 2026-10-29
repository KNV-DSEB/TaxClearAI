import { ReactNode } from 'react';
import { Check, X } from 'lucide-react';

import { cn } from '@/utils/cn';

export type StepStatus = 'wait' | 'process' | 'finish' | 'error';

export type StepItem = {
  title: ReactNode;
  description?: ReactNode;
  icon?: ReactNode;
  // Overrides the status this step would otherwise get from its position
  // relative to `current` — for a step that failed independently of where
  // the process currently is (e.g. import row 3 errored while step 4 runs).
  status?: StepStatus;
  disabled?: boolean;
};

type StepsProps = {
  items: StepItem[];
  current?: number;
  direction?: 'horizontal' | 'vertical';
  size?: 'default' | 'small';
  onChange?: (index: number) => void;
  className?: string;
};

function resolveStatus(item: StepItem, index: number, current: number): StepStatus {
  if (item.status) return item.status;
  if (index < current) return 'finish';
  if (index === current) return 'process';
  return 'wait';
}

function StepIcon({ status, icon, index, size }: { status: StepStatus; icon?: ReactNode; index: number; size: 'default' | 'small' }) {
  const dimension = size === 'small' ? 'h-6 w-6 text-xs' : 'h-8 w-8 text-sm';

  if (icon) {
    return (
      <span className={cn('flex shrink-0 items-center justify-center rounded-full', dimension, 'bg-primary/10 text-primary')}>
        {icon}
      </span>
    );
  }

  if (status === 'finish') {
    return (
      <span className={cn('flex shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground', dimension)}>
        <Check className={size === 'small' ? 'h-3 w-3' : 'h-3.5 w-3.5'} aria-hidden />
      </span>
    );
  }

  if (status === 'error') {
    return (
      <span className={cn('flex shrink-0 items-center justify-center rounded-full bg-destructive text-destructive-foreground', dimension)}>
        <X className={size === 'small' ? 'h-3 w-3' : 'h-3.5 w-3.5'} aria-hidden />
      </span>
    );
  }

  return (
    <span
      className={cn(
        'flex shrink-0 items-center justify-center rounded-full border font-semibold',
        dimension,
        status === 'process' ? 'border-primary text-primary' : 'border-border text-muted-foreground'
      )}
    >
      {index + 1}
    </span>
  );
}

function StepLabel({ item, status }: { item: StepItem; status: StepStatus }) {
  return (
    <span className="flex min-w-0 flex-col">
      <span
        className={cn(
          'truncate text-sm',
          status === 'wait' ? 'text-muted-foreground' : 'font-medium text-foreground',
          status === 'error' && 'text-destructive'
        )}
      >
        {item.title}
      </span>
      {item.description && <span className="truncate text-xs text-muted-foreground">{item.description}</span>}
    </span>
  );
}

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics". Mirrors antd's Steps: an ordered list of stages in a
// process, each auto-classified wait/process/finish relative to `current`
// unless a step's own `status` overrides it (e.g. a step that failed).
export function Steps({ items, current = 0, direction = 'horizontal', size = 'default', onChange, className }: StepsProps) {
  return (
    <div className={cn(direction === 'horizontal' ? 'flex w-full' : 'flex flex-col gap-6', className)}>
      {items.map((item, index) => {
        const status = resolveStatus(item, index, current);
        const clickable = !!onChange && !item.disabled;
        const isLast = index === items.length - 1;

        const body = (
          <>
            <div className="flex flex-col items-center">
              <StepIcon status={status} icon={item.icon} index={index} size={size} />
              {direction === 'vertical' && !isLast && <span className="mt-2 w-px flex-1 bg-border" />}
            </div>
            <span className={cn('flex min-w-0 items-center', direction === 'horizontal' ? 'ml-3' : 'ml-3 pb-6')}>
              <StepLabel item={item} status={status} />
            </span>
          </>
        );

        return (
          <div
            key={index}
            className={cn(direction === 'horizontal' ? 'flex flex-1 items-start' : 'flex items-start')}
          >
            {clickable ? (
              <button
                type="button"
                onClick={() => onChange(index)}
                className={cn('flex items-start text-left', direction === 'horizontal' && 'flex-1')}
              >
                {body}
              </button>
            ) : (
              <div className={cn('flex items-start', direction === 'horizontal' && 'flex-1')}>{body}</div>
            )}
            {direction === 'horizontal' && !isLast && (
              <span className={cn('mx-3 mt-4 h-px flex-1', status === 'finish' ? 'bg-primary' : 'bg-border')} />
            )}
          </div>
        );
      })}
    </div>
  );
}
