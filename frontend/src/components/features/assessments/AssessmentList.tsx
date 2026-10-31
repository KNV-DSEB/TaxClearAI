'use client';

import { ArrowRight, Plus, Trash2 } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import { ApiError } from '@/services/api.client';
import { assessmentsService } from '@/services/assessments.service';
import type { AssessmentListItem, AssessmentPage, CaseFilter } from '@/types/api.types';

import { SCOPE_TITLES, STATUS_LABELS, formatDate } from './case-status';
import { CaseSidebar, filterHref } from './CaseSidebar';

const EMPTY_TEXT: Record<CaseFilter, string> = {
  all: 'Chưa có hồ sơ nào được lưu.',
  in_progress: 'Không có hồ sơ nào đang thực hiện.',
  ready: 'Chưa có hồ sơ nào đủ giấy tờ.',
};

function CaseCard({ item, onRemove }: { item: AssessmentListItem; onRemove: () => Promise<void> }) {
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const { available, missing, needsVerification } = item.counts;
  const total = available + missing + needsVerification;

  async function remove(): Promise<void> {
    setBusy(true);
    try {
      await onRemove();
    } finally {
      setBusy(false);
    }
  }

  return (
    <li className="card case-card">
      <div className="case-card-main">
        <div className="case-card-title">
          <h2>Hồ sơ: {SCOPE_TITLES[item.scope]}</h2>
          <span className={`badge badge-${item.status}`}>{STATUS_LABELS[item.status]}</span>
        </div>
        <p className="small muted">
          Tạo {formatDate(item.createdAt)} ·{' '}
          {item.expired
            ? 'đã hết hạn truy cập, bạn vẫn có thể xóa'
            : `cập nhật ${formatDate(item.updatedAt, true)} · lưu đến ${formatDate(item.expiresAt)}`}
        </p>
        {item.scope === 'b2' && total > 0 && (
          <div className="case-progress">
            <progress
              className="progress"
              value={available}
              max={total}
              aria-label="Giấy tờ đã có"
            />
            <span className="case-counts">
              {available} đã có · {missing} còn thiếu · {needsVerification} cần xác minh
            </span>
          </div>
        )}
      </div>
      <div className="case-card-actions">
        {!item.expired && (
          <Link className="button button-secondary" href={`/ho-so/${item.id}`}>
            Mở hồ sơ <ArrowRight size={16} />
          </Link>
        )}
        <button className="text-link destructive" onClick={() => setConfirming(true)}>
          <Trash2 size={15} /> Xóa
        </button>
      </div>
      {confirming && (
        <div className="delete-confirm" role="group" aria-label="Xác nhận xóa">
          <p>Xóa toàn bộ câu trả lời và checklist của hồ sơ này? Không thể hoàn tác.</p>
          <button
            className="button button-danger"
            disabled={busy}
            onClick={() => {
              void remove();
            }}
          >
            {busy ? 'Đang xóa…' : 'Xác nhận xóa hồ sơ'}
          </button>
          <button
            className="button button-quiet"
            disabled={busy}
            onClick={() => setConfirming(false)}
          >
            Giữ hồ sơ
          </button>
        </div>
      )}
    </li>
  );
}

export function AssessmentList({ filter = 'all' }: { filter?: CaseFilter }) {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [data, setData] = useState<AssessmentPage | null>(null);
  const [error, setError] = useState('');
  const [reload, setReload] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    async function load(): Promise<void> {
      try {
        setData(await assessmentsService.list(page, filter, controller.signal));
        setError('');
      } catch (error) {
        if (controller.signal.aborted) return;
        if (error instanceof ApiError && error.status === 401)
          router.replace(`/dang-nhap?returnTo=${encodeURIComponent('/ho-so')}`);
        else setError(error instanceof Error ? error.message : 'Chưa tải được danh sách hồ sơ.');
      }
    }
    void load();
    return () => controller.abort();
  }, [page, filter, reload, router]);

  async function remove(id: string): Promise<void> {
    try {
      await assessmentsService.remove(id);
      // Xóa phần tử cuối của một trang thì lùi về trang trước để không thấy trang rỗng
      if (data && data.items.length === 1 && page > 1) setPage(page - 1);
      else setReload((value) => value + 1);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Chưa xóa được. Vui lòng thử lại.');
    }
  }

  const lastPage = data ? Math.max(1, Math.ceil(data.total / data.pageSize)) : 1;

  return (
    <div className="case-layout">
      <CaseSidebar active={filter} counts={data?.statusCounts ?? null} />
      <section className="case-main">
        <div className="page-heading">
          <div>
            <h1>Hồ sơ của tôi</h1>
            <p className="muted">Tiếp tục từ chỗ bạn đã dừng. Hồ sơ mới cập nhật nằm trên cùng.</p>
          </div>
          <Link className="button button-primary" href="/khao-sat">
            <Plus size={16} /> Chuẩn bị hồ sơ mới
          </Link>
        </div>
        {error && (
          <p role="alert" className="error-message">
            {error}
          </p>
        )}
        {!data && !error && (
          <p role="status" className="muted">
            Đang tải danh sách hồ sơ…
          </p>
        )}
        {data && data.total === 0 && (
          <div className="card empty-card">
            <h2>{EMPTY_TEXT[filter]}</h2>
            {filter === 'all' ? (
              <>
                <p>Trả lời 11 câu hỏi để có bản tổng hợp và checklist chuẩn bị khảo sát.</p>
                <Link className="button button-primary" href="/khao-sat">
                  Bắt đầu chuẩn bị hồ sơ <ArrowRight size={16} />
                </Link>
              </>
            ) : (
              <Link className="button button-secondary" href={filterHref('all')}>
                Xem tất cả hồ sơ
              </Link>
            )}
          </div>
        )}
        {data && data.items.length > 0 && (
          <ul className="case-list" aria-label="Danh sách hồ sơ">
            {data.items.map((item) => (
              <CaseCard key={item.id} item={item} onRemove={() => remove(item.id)} />
            ))}
          </ul>
        )}
        {lastPage > 1 && (
          <nav className="case-pagination" aria-label="Phân trang hồ sơ">
            <button
              className="button button-quiet"
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
            >
              Trang trước
            </button>
            <span className="small muted">
              Trang {page}/{lastPage}
            </span>
            <button
              className="button button-quiet"
              disabled={page >= lastPage}
              onClick={() => setPage(page + 1)}
            >
              Trang sau
            </button>
          </nav>
        )}
      </section>
    </div>
  );
}
