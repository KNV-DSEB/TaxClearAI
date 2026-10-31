'use client';

import {
  ArrowRight,
  Check,
  CircleAlert,
  CircleCheck,
  ClipboardList,
  Download,
  PencilLine,
  Plus,
  Trash2,
} from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { assessmentsService } from '@/services/assessments.service';
import type { Assessment, ItemStatus } from '@/types/api.types';

import { CaseSidebar } from './CaseSidebar';
import { SCOPE_TITLES, STATUS_LABELS, caseStatus, formatDate } from './case-status';

type WorkspaceAssessment = Omit<Assessment, 'answers'>;

// Hồ sơ lưu từ phiên bản cũ còn nhãn cũ cho mục này
function itemLabel(item: Assessment['checklist'][number]): string {
  return item.code === 'purchase_schedules' ? 'Bảng kê mua hàng theo kỳ áp dụng' : item.label;
}

const STEPS = ['Trả lời khảo sát', 'Xem kết quả', 'Chuẩn bị hồ sơ', 'Đủ giấy tờ'];

function Stepper({ reached }: { reached: number }) {
  return (
    <ol className="stepper" aria-label="Tiến trình hồ sơ">
      {STEPS.map((label, index) => {
        const state = index < reached ? 'done' : index === reached ? 'current' : 'todo';
        return (
          <li key={label} className={state} aria-current={state === 'current' ? 'step' : undefined}>
            <span className="step-dot">{state === 'done' ? <Check size={16} /> : index + 1}</span>
            <span className="step-label">{label}</span>
          </li>
        );
      })}
    </ol>
  );
}

function summaryHeadline(assessment: WorkspaceAssessment): { title: string; detail: string } {
  const reasons = assessment.summary.reviewReasons.length;
  if (assessment.summary.scope === 'b2')
    return {
      title: 'Doanh nghiệp từng hoạt động, muốn giải thể',
      detail: reasons
        ? `${reasons} điểm cần chuyên viên xác minh trước khi làm thủ tục.`
        : 'Chuyên viên vẫn cần xác minh trước khi làm thủ tục.',
    };
  if (assessment.summary.scope === 'needs_confirmation')
    return {
      title: 'Chưa đủ thông tin để xác định phạm vi',
      detail: 'Hãy trao đổi với chuyên viên hoặc làm lại khảo sát.',
    };
  return {
    title: 'Tình huống nằm ngoài phạm vi bản thử',
    detail: 'Bản thử chỉ hỗ trợ doanh nghiệp từng hoạt động muốn giải thể.',
  };
}

export function AssessmentWorkspace({ initial }: { initial: WorkspaceAssessment }) {
  const router = useRouter();
  const [assessment, setAssessment] = useState(initial);
  const [saving, setSaving] = useState('');
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [busy, setBusy] = useState(false);

  const status = caseStatus(assessment);
  const inScope = assessment.summary.scope === 'b2';
  const remaining = assessment.checklist.filter((item) => item.status !== 'available').length;
  const available = assessment.checklist.length - remaining;
  const headline = summaryHeadline(assessment);
  const reached = !inScope ? 1 : status === 'ready' ? 4 : 2;

  async function update(itemId: string, value: ItemStatus): Promise<void> {
    setSaving(itemId);
    setNotice('');
    setError('');
    try {
      const updated = await assessmentsService.updateItem(assessment.id, itemId, value);
      setAssessment((current) => ({
        ...current,
        updatedAt: new Date().toISOString(),
        checklist: current.checklist.map((item) => (item.id === itemId ? updated : item)),
      }));
      setNotice('Đã lưu trạng thái hồ sơ.');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Chưa lưu được. Vui lòng thử lại.');
    } finally {
      setSaving('');
    }
  }

  async function remove(): Promise<void> {
    setBusy(true);
    setError('');
    try {
      await assessmentsService.remove(assessment.id);
      router.replace('/ho-so');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Chưa xóa được. Vui lòng thử lại.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="case-layout">
      <CaseSidebar />
      <section className="case-main">
        <div className="page-heading">
          <div>
            <div className="case-card-title">
              <h1>Hồ sơ: {SCOPE_TITLES[assessment.summary.scope]}</h1>
              <span className={`badge badge-${status}`}>{STATUS_LABELS[status]}</span>
            </div>
            <p className="small muted">Cập nhật: {formatDate(assessment.updatedAt, true)}</p>
          </div>
        </div>

        <div className="card stepper-card">
          <Stepper reached={reached} />
        </div>

        <div className="overview-grid">
          <div className="card overview-card">
            <h2>Tổng hợp tình trạng</h2>
            <div className="overview-body">
              {inScope ? (
                <CircleCheck className="overview-icon ok" size={30} />
              ) : (
                <CircleAlert className="overview-icon warn" size={30} />
              )}
              <div>
                <strong>{headline.title}</strong>
                <p className="small muted">{headline.detail}</p>
              </div>
            </div>
          </div>
          <div className="card overview-card">
            <h2>Checklist hồ sơ cần chuẩn bị</h2>
            {inScope ? (
              <>
                <p>
                  {remaining > 0
                    ? `${remaining} mục cần chuẩn bị · ${available}/${assessment.checklist.length} đã có`
                    : `Đã có đủ ${assessment.checklist.length} mục giấy tờ`}
                </p>
                <a className="text-link" href="#checklist">
                  Xem chi tiết <ArrowRight size={14} />
                </a>
              </>
            ) : (
              <p className="small muted">Chưa áp dụng danh mục cho phạm vi này.</p>
            )}
          </div>
        </div>

        <div className="case-actions">
          {inScope && (
            <a className="button button-outline" href="#checklist">
              <PencilLine size={16} /> Cập nhật giấy tờ
            </a>
          )}
          <Link className="button button-primary" href={`/ho-so/${assessment.id}/ban-in`}>
            <Download size={16} /> Tải bản tổng hợp
          </Link>
        </div>

        <section className="card checklist-card" id="checklist" aria-labelledby="checklist-heading">
          <div className="panel-heading">
            <h2 id="checklist-heading">
              <ClipboardList size={20} /> Danh mục chuẩn bị
            </h2>
            {inScope && (
              <span className="small muted">
                {available} / {assessment.checklist.length} đã có
              </span>
            )}
          </div>
          {assessment.checklist.length > 0 ? (
            <ul className="checklist">
              {assessment.checklist.map((item) => {
                const label = itemLabel(item);
                return (
                  <li key={item.id}>
                    <span
                      className={`check-indicator ${item.status === 'available' ? 'done' : ''}`}
                      aria-hidden="true"
                    >
                      {item.status === 'available' ? <Check size={14} /> : null}
                    </span>
                    <strong>{label}</strong>
                    <select
                      name={item.code}
                      aria-label={`Trạng thái: ${label}`}
                      value={item.status}
                      disabled={saving !== '' || busy}
                      onChange={(event) => {
                        void update(item.id, event.target.value as ItemStatus);
                      }}
                    >
                      <option value="available">Đã có</option>
                      <option value="missing">Còn thiếu</option>
                      <option value="needs_verification">Cần xác minh</option>
                    </select>
                  </li>
                );
              })}
            </ul>
          ) : (
            <div className="empty-inline">
              <h3>Cần xác nhận phạm vi trước.</h3>
              <p className="small muted">
                Câu trả lời hiện chưa đủ để áp dụng danh mục doanh nghiệp từng hoạt động muốn giải
                thể. Hãy trao đổi với chuyên viên hoặc mở khảo sát mới.
              </p>
            </div>
          )}
          {saving && (
            <p role="status" className="small muted">
              Đang lưu trạng thái…
            </p>
          )}
          <p role="status" aria-live="polite" className="success-message">
            {notice}
          </p>
          {error && (
            <p role="alert" className="error-message">
              {error}
            </p>
          )}
        </section>

        <div className="overview-grid">
          <section className="card detail-card">
            <h2>Những điều cần làm rõ</h2>
            {assessment.summary.reviewReasons.length > 0 ? (
              <ul className="review-list">
                {assessment.summary.reviewReasons.map((text) => (
                  <li key={text}>{text}</li>
                ))}
              </ul>
            ) : (
              <p className="small muted">Mở thông tin đã ghi nhận để xem lại câu trả lời.</p>
            )}
            <details>
              <summary>Thông tin chưa biết ({assessment.summary.unknownFacts.length})</summary>
              <ul>
                {assessment.summary.unknownFacts.map((text) => (
                  <li key={text}>{text}</li>
                ))}
              </ul>
            </details>
            <details>
              <summary>Thông tin đã ghi nhận</summary>
              <ul>
                {assessment.summary.knownFacts.map((text) => (
                  <li key={text}>{text}</li>
                ))}
              </ul>
            </details>
          </section>
          <section className="card detail-card">
            <h2>Quản lý hồ sơ thử</h2>
            <p className="small muted">
              Lưu đến {formatDate(assessment.expiresAt)}. Chỉ sử dụng dữ liệu giả định.
            </p>
            <Link className="text-link" href="/khao-sat">
              <Plus size={16} /> Chuẩn bị hồ sơ khác
            </Link>
            <button className="text-link destructive" onClick={() => setConfirmDelete(true)}>
              <Trash2 size={15} /> Xóa hồ sơ thử này
            </button>
            {confirmDelete && (
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
                  onClick={() => setConfirmDelete(false)}
                >
                  Giữ hồ sơ
                </button>
              </div>
            )}
          </section>
        </div>
      </section>
    </div>
  );
}
