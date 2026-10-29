import { HTMLAttributes, ReactNode } from 'react';

import { cn } from '@/utils/cn';

type EmptyProps = HTMLAttributes<HTMLDivElement> & {
  description?: ReactNode;
  image?: ReactNode;
};

function DefaultEmptyImage() {
  return (
    <svg
      className="h-16 w-16 text-muted-foreground"
      viewBox="0 0 64 41"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <path
        d="M55.5 12.5L44.5 1H19.5L8.5 12.5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <rect x="0.75" y="12.75" width="62.5" height="27.5" rx="3.25" stroke="currentColor" strokeWidth="1.5" />
      <path
        d="M0.75 25H19a3 3 0 0 1 2.83 2H41.17a3 3 0 0 1 2.83-2h18.25"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics".
export function Empty({ description = 'No data', image, className, children, ...props }: EmptyProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 py-10', className)} {...props}>
      {image ?? <DefaultEmptyImage />}
      {description && <div className="text-sm text-muted-foreground">{description}</div>}
      {children}
    </div>
  );
}
