'use client';

import { ArrowRight, Plus, Trash2 } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import { ApiError } from '@/services/api.client';
import { assessmentsService } from '@/services/assessments.service';
import type { AssessmentListItem, AssessmentPage } from '@/types/api.types';

const SCOPE_LABELS: Record<AssessmentListItem['scope'], string> = {
  b2: 'Doanh nghiệp muốn giải thể',
  needs_confirmation: 'Cần xác nhận phạm vi',
  out_of_scope: 'Ngoài phạm vi bản thử',
};

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('vi-VN', { dateStyle: 'medium' }).format(new Date(value));
}

function CaseCard({ item, onRemove }: { item: AssessmentListItem; onRemove: () => Promise<void> }) {
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const { available, missing, needsVerification } = item.counts;

  async function remove(): Promise<void> {
    setBusy(true);
    try {
      await onRemove();
    } finally {
      setBusy(false);
    }
  }

  return (
    <li className="surface case-card">
      <div className="case-card-main">
        <span className="section-kicker">{SCOPE_LABELS[item.scope]}</span>
        <h2>Hồ sơ tạo ngày {formatDate(item.createdAt)}</h2>
        {item.scope === 'b2' && (
          <p className="case-counts">
            {available} đã có · {missing} còn thiếu · {needsVerification} cần xác minh
          </p>
        )}
        <p className="small muted">
          {item.expired
            ? 'Đã hết hạn truy cập. Bạn vẫn có thể xóa hồ sơ này.'
            : `Cập nhật ${formatDate(item.updatedAt)} · lưu đến ${formatDate(item.expiresAt)}`}
        </p>
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

export function AssessmentList() {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [data, setData] = useState<AssessmentPage | null>(null);
  const [error, setError] = useState('');
  const [reload, setReload] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    async function load(): Promise<void> {
      try {
        setData(await assessmentsService.list(page, controller.signal));
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
  }, [page, reload, router]);

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
    <>
      <div className="workspace-heading">
        <div>
          <span className="section-kicker">Hồ sơ của tôi</span>
          <h1>Tiếp tục từ chỗ bạn đã dừng.</h1>
          <p className="muted">Các hồ sơ thử bạn đã lưu, mới cập nhật nằm trên cùng.</p>
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
        <p role="status" className="muted case-loading">
          Đang tải danh sách hồ sơ…
        </p>
      )}
      {data && data.total === 0 && (
        <section className="surface empty-state case-empty">
          <h2>Chưa có hồ sơ nào được lưu.</h2>
          <p>Trả lời 11 câu hỏi để có bản tổng hợp và checklist chuẩn bị khảo sát.</p>
          <Link className="button button-primary" href="/khao-sat">
            Bắt đầu chuẩn bị hồ sơ <ArrowRight size={16} />
          </Link>
        </section>
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
    </>
  );
}
