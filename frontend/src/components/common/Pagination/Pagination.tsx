'use client';

import { useState } from 'react';

import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Select } from '@/components/common/Select';
import { cn } from '@/utils/cn';

const DEFAULT_PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

export type PaginationProps = {
  page: number;
  size: number;
  total: number;
  onPageChange: (page: number) => void;
  onSizeChange: (size: number) => void;
  pageSizeOptions?: number[];
  className?: string;
};

type PageItem = number | 'ellipsis';

// Windows down to first/last + neighbors of the current page once there are
// too many pages to list in full — mirrors db-sync-service's Pagination.
function getPageList(current: number, totalPages: number): PageItem[] {
  if (totalPages <= 7) {
    return Array.from({ length: totalPages }, (_, i) => i + 1);
  }

  const left = Math.max(2, current - 1);
  const right = Math.min(totalPages - 1, current + 1);
  const items: PageItem[] = [1];

  if (left > 2) {
    items.push('ellipsis');
  } else if (left === 3) {
    items.push(2);
  }

  for (let p = left; p <= right; p += 1) {
    items.push(p);
  }

  if (right < totalPages - 1) {
    items.push('ellipsis');
  } else if (right === totalPages - 2) {
    items.push(totalPages - 1);
  }

  items.push(totalPages);
  return items;
}

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics".
export function Pagination({
  page,
  size,
  total,
  onPageChange,
  onSizeChange,
  pageSizeOptions = DEFAULT_PAGE_SIZE_OPTIONS,
  className,
}: PaginationProps) {
  const [goInput, setGoInput] = useState('');
  const totalPages = Math.max(1, Math.ceil(total / size));

  function submitGo() {
    const target = Number(goInput);
    if (Number.isInteger(target) && target >= 1 && target <= totalPages) {
      onPageChange(target);
      setGoInput('');
    }
  }

  if (total === 0) {
    return (
      <div className={cn('flex items-center justify-end text-sm text-muted-foreground', className)}>
        Tổng: 0 bản ghi
      </div>
    );
  }

  const sizeOptions = pageSizeOptions.map((option) => ({ value: String(option), label: `${option} / trang` }));

  return (
    <div className={cn('flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between', className)}>
      <span className="text-sm text-muted-foreground">Tổng: {total} bản ghi</span>

      <div className="flex flex-wrap items-center gap-1">
        <Button size="sm" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
          Trước
        </Button>
        {getPageList(page, totalPages).map((item, index) =>
          item === 'ellipsis' ? (
            <span key={`ellipsis-${index}`} className="px-2 text-muted-foreground">
              …
            </span>
          ) : (
            <Button key={item} type={item === page ? 'primary' : 'default'} size="sm" onClick={() => onPageChange(item)}>
              {item}
            </Button>
          )
        )}
        <Button size="sm" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>
          Sau
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          size="sm"
          className="w-16"
          value={goInput}
          onChange={(e) => setGoInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') submitGo();
          }}
          placeholder="Trang"
        />
        <Button size="sm" onClick={submitGo}>
          Đi tới
        </Button>

        <Select
          size="sm"
          className="w-28"
          options={sizeOptions}
          value={String(size)}
          onChange={(v) => v && onSizeChange(Number(v))}
        />
      </div>
    </div>
  );
}
