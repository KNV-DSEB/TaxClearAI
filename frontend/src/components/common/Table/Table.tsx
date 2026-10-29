'use client';

import { ReactNode, useMemo, useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

import { Empty } from '@/components/common/Empty';
import { Pagination } from '@/components/common/Pagination';
import { cn } from '@/utils/cn';

export type TableColumn<T> = {
  key: string;
  title: ReactNode;
  dataIndex?: keyof T;
  render?: (value: unknown, record: T, index: number) => ReactNode;
  width?: number | string;
  align?: 'left' | 'center' | 'right';
  sorter?: (a: T, b: T) => number;
};

export type TablePagination = {
  current: number;
  pageSize: number;
  total: number;
  onChange: (page: number, pageSize: number) => void;
};

type TableProps<T> = {
  columns: TableColumn<T>[];
  dataSource: T[];
  rowKey: keyof T | ((record: T) => string);
  loading?: boolean;
  pagination?: TablePagination;
  emptyText?: ReactNode;
  className?: string;
  onRowClick?: (record: T) => void;
};

const alignClass: Record<NonNullable<TableColumn<unknown>['align']>, string> = {
  left: 'text-left',
  center: 'text-center',
  right: 'text-right',
};

function getRowKey<T>(record: T, rowKey: TableProps<T>['rowKey'], index: number): string {
  if (typeof rowKey === 'function') {
    return rowKey(record);
  }
  return String(record[rowKey] ?? index);
}

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics".
export function Table<T>({
  columns,
  dataSource,
  rowKey,
  loading = false,
  pagination,
  emptyText,
  className,
  onRowClick,
}: TableProps<T>) {
  const [sortState, setSortState] = useState<{ key: string; order: 'asc' | 'desc' } | null>(null);

  const sortedData = useMemo(() => {
    if (!sortState) {
      return dataSource;
    }
    const column = columns.find((c) => c.key === sortState.key);
    if (!column?.sorter) {
      return dataSource;
    }
    const sorted = [...dataSource].sort(column.sorter);
    return sortState.order === 'asc' ? sorted : sorted.reverse();
  }, [dataSource, sortState, columns]);

  const toggleSort = (column: TableColumn<T>) => {
    if (!column.sorter) {
      return;
    }
    setSortState((prev) => {
      if (prev?.key !== column.key) {
        return { key: column.key, order: 'asc' };
      }
      return prev.order === 'asc' ? { key: column.key, order: 'desc' } : null;
    });
  };

  return (
    <div className={cn('w-full', className)}>
      <div className="overflow-x-auto rounded-md border border-border">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/50">
              {columns.map((column) => (
                <th
                  key={column.key}
                  style={{ width: column.width }}
                  className={cn(
                    'px-3 py-2 font-medium text-muted-foreground',
                    alignClass[column.align ?? 'left'],
                    column.sorter && 'cursor-pointer select-none'
                  )}
                  onClick={() => toggleSort(column)}
                >
                  <span className="inline-flex items-center gap-1">
                    {column.title}
                    {column.sorter &&
                      (sortState?.key === column.key ? (
                        sortState.order === 'asc' ? (
                          <ChevronUp className="h-3.5 w-3.5" aria-hidden />
                        ) : (
                          <ChevronDown className="h-3.5 w-3.5" aria-hidden />
                        )
                      ) : (
                        <ChevronDown className="h-3.5 w-3.5 opacity-30" aria-hidden />
                      ))}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={columns.length} className="py-10 text-center text-sm text-muted-foreground">
                  Loading...
                </td>
              </tr>
            ) : sortedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="p-0">
                  <Empty description={emptyText} />
                </td>
              </tr>
            ) : (
              sortedData.map((record, index) => (
                <tr
                  key={getRowKey(record, rowKey, index)}
                  onClick={onRowClick ? () => onRowClick(record) : undefined}
                  className={cn(
                    'border-b border-border last:border-0 hover:bg-accent/50',
                    onRowClick && 'cursor-pointer'
                  )}
                >
                  {columns.map((column) => {
                    const value = column.dataIndex ? record[column.dataIndex] : undefined;
                    return (
                      <td key={column.key} className={cn('px-3 py-2 text-foreground', alignClass[column.align ?? 'left'])}>
                        {column.render ? column.render(value, record, index) : (value as ReactNode)}
                      </td>
                    );
                  })}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {pagination && (
        <Pagination
          className="mt-3"
          page={pagination.current}
          size={pagination.pageSize}
          total={pagination.total}
          onPageChange={(page) => pagination.onChange(page, pagination.pageSize)}
          onSizeChange={(size) => pagination.onChange(1, size)}
        />
      )}
    </div>
  );
}
