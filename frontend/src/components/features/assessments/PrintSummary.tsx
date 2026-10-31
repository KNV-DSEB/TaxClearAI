'use client';

import { ArrowLeft, CircleCheck, Download, Printer } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import { ApiError } from '@/services/api.client';
import { assessmentsService } from '@/services/assessments.service';
import type { Assessment, ItemStatus } from '@/types/api.types';

import { SCOPE_TITLES, STATUS_LABELS, caseStatus, formatDate } from './case-status';

const ITEM_STATUS: Record<ItemStatus, string> = {
  available: 'Đã có',
  missing: 'Còn thiếu',
  needs_verification: 'Cần xác minh',
};

export function PrintSummary({ id }: { id: string }) {
  const router = useRouter();
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    assessmentsService
      .get(id, controller.signal)
      .then(setAssessment)
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;
        if (error instanceof ApiError && error.status === 401)
          router.replace(`/dang-nhap?returnTo=${encodeURIComponent(`/ho-so/${id}`)}`);
        else setError(error instanceof Error ? error.message : 'Chưa mở được bản tổng hợp.');
      });
    return () => controller.abort();
  }, [id, router]);

  if (!assessment)
    return (
      <section className="card loading-panel">
        {error ? <p role="alert">{error}</p> : <p role="status">Đang chuẩn bị bản tổng hợp…</p>}
      </section>
    );

  const status = caseStatus(assessment);
  return (
    <div className="print-page">
      <div className="page-heading no-print">
        <div>
          <Link className="text-link" href={`/ho-so/${assessment.id}`}>
            <ArrowLeft size={15} /> Về hồ sơ
          </Link>
          <h1>Bản in tổng hợp</h1>
          <p className="muted">Xem, in hoặc lưu bản tổng hợp để làm việc với chuyên viên.</p>
        </div>
        <button className="button button-outline" onClick={() => window.print()}>
          <Download size={16} /> Lưu PDF
        </button>
      </div>
      <article className="card print-sheet">
        <div className="print-ready no-print">
          <CircleCheck size={44} />
          <h2>Bản tổng hợp đã sẵn sàng</h2>
          <p className="muted">
            Chọn “In bản tổng hợp”. Muốn lưu file, chọn “Lưu dưới dạng PDF” trong hộp thoại in.
          </p>
        </div>
        <h2 className="print-only">Tax Clear AI — Bản tổng hợp hồ sơ</h2>
        <section>
          <h3>Thông tin hồ sơ</h3>
          <dl className="print-facts">
            <dt>Loại hồ sơ</dt>
            <dd>{SCOPE_TITLES[assessment.summary.scope]}</dd>
            <dt>Ngày tạo</dt>
            <dd>{formatDate(assessment.createdAt)}</dd>
            <dt>Cập nhật</dt>
            <dd>{formatDate(assessment.updatedAt, true)}</dd>
            <dt>Trạng thái</dt>
            <dd>
              <span className={`badge badge-${status}`}>{STATUS_LABELS[status]}</span>
            </dd>
          </dl>
        </section>
        {assessment.summary.reviewReasons.length > 0 && (
          <section>
            <h3>Điểm cần chuyên viên xác minh</h3>
            <ul>
              {assessment.summary.reviewReasons.map((text) => (
                <li key={text}>{text}</li>
              ))}
            </ul>
          </section>
        )}
        <section>
          <h3>Thông tin đã ghi nhận</h3>
          <ul>
            {assessment.summary.knownFacts.map((text) => (
              <li key={text}>{text}</li>
            ))}
          </ul>
        </section>
        {assessment.summary.unknownFacts.length > 0 && (
          <section>
            <h3>Thông tin chưa biết</h3>
            <ul>
              {assessment.summary.unknownFacts.map((text) => (
                <li key={text}>{text}</li>
              ))}
            </ul>
          </section>
        )}
        {assessment.checklist.length > 0 && (
          <section>
            <h3>Danh mục giấy tờ</h3>
            <table className="print-table">
              <thead>
                <tr>
                  <th scope="col">Giấy tờ</th>
                  <th scope="col">Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                {assessment.checklist.map((item) => (
                  <tr key={item.id}>
                    <td>{item.label}</td>
                    <td>{ITEM_STATUS[item.status]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
        <p className="small muted print-notice">
          {assessment.summary.notice} Bản tổng hợp không phải kết luận pháp lý.
        </p>
        <button
          className="button button-outline button-block no-print"
          onClick={() => window.print()}
        >
          <Printer size={16} /> In bản tổng hợp
        </button>
      </article>
    </div>
  );
}
