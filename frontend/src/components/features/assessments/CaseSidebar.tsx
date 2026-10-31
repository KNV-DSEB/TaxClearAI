'use client';

import { CircleCheck, FolderOpen, Hourglass, MessagesSquare } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';

import { assessmentsService } from '@/services/assessments.service';
import type { CaseFilter, StatusCounts } from '@/types/api.types';

const FILTERS: {
  value: CaseFilter;
  label: string;
  icon: typeof FolderOpen;
  key: keyof StatusCounts;
}[] = [
  { value: 'all', label: 'Tất cả hồ sơ', icon: FolderOpen, key: 'all' },
  { value: 'in_progress', label: 'Đang thực hiện', icon: Hourglass, key: 'inProgress' },
  { value: 'ready', label: 'Đã đủ giấy tờ', icon: CircleCheck, key: 'ready' },
];

export function filterHref(filter: CaseFilter): string {
  return filter === 'all' ? '/ho-so' : `/ho-so?trang-thai=${filter}`;
}

export function CaseSidebar({
  active,
  counts: provided,
}: {
  active?: CaseFilter;
  // undefined: tự tải bộ đếm; null: trang cha đang tải và sẽ truyền xuống
  counts?: StatusCounts | null;
}) {
  const [loaded, setLoaded] = useState<StatusCounts | null>(null);
  const counts = provided ?? loaded;

  useEffect(() => {
    if (provided !== undefined) return;
    const controller = new AbortController();
    assessmentsService
      .list(1, 'all', controller.signal)
      .then((page) => setLoaded(page.statusCounts))
      .catch(() => setLoaded(null));
    return () => controller.abort();
  }, [provided]);

  return (
    <aside className="card case-sidebar" aria-label="Lọc hồ sơ">
      <p className="sidebar-title">Hồ sơ của tôi</p>
      <ul>
        {FILTERS.map(({ value, label, icon: Icon, key }) => (
          <li key={value}>
            <Link
              href={filterHref(value)}
              aria-current={active === value ? 'page' : undefined}
              className="sidebar-link"
            >
              <Icon size={16} />
              <span>{label}</span>
              {counts && <span className="count">{counts[key]}</span>}
            </Link>
          </li>
        ))}
      </ul>
      <Link className="sidebar-chat" href="/hoi-dap">
        <MessagesSquare size={18} />
        <span>
          <strong>Có câu hỏi về thủ tục?</strong>
          <span>Hỏi đáp cùng AI, kèm trích dẫn văn bản.</span>
        </span>
      </Link>
    </aside>
  );
}
