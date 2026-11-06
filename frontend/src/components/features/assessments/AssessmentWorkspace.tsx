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
  Tags,
  Trash2,
  UserCheck,
} from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import { PlanDialog } from '@/components/features/pricing/PlanDialog';
import { assessmentsService } from '@/services/assessments.service';
import type { Assessment, ItemStatus } from '@/types/api.types';
import { clearPlanPrompt, peekPlanPrompt } from '@/utils/plan-prompt';
import { RecommendedExpertsSection } from '@/components/features/experts/RecommendedExpertsSection';

import { CaseSidebar } from './CaseSidebar';
import { IN_SCOPE, SCOPE_TITLES, STATUS_LABELS, caseStatus, formatDate } from './case-status';

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
  const headlines: Partial<
    Record<Assessment['summary']['scope'], { title: string; detail: string }>
  > = {
    a1: {
      title: 'Hộ kinh doanh chưa đăng ký',
      detail: 'Cần làm việc với cơ quan thuế để hợp thức hóa hoặc chấm dứt.',
    },
    a2: {
      title: 'Hộ kinh doanh có đăng ký nhưng chưa hoàn tất kê khai',
      detail: 'Cần hoàn tất chấm dứt hộ cũ trước khi đăng ký hộ mới.',
    },
    a3: {
      title: 'Hộ kinh doanh có rủi ro sai lệch kê khai',
      detail: 'Hồ sơ có dấu hiệu chênh lệch số liệu; khuyến nghị trao đổi với chuyên gia thuế.',
    },
    b1: {
      title: 'Doanh nghiệp chưa phát sinh doanh số',
      detail: 'Quy trình giải thể đơn giản hoặc chuẩn bị hồ sơ chuyển nhượng/tái cấu trúc.',
    },
    b2: {
      title: 'Doanh nghiệp đã hoạt động, giải thể có tồn đọng',
      detail: 'Cần rà soát quyết toán thuế, VAT và thanh lý tài sản.',
    },
    needs_confirmation: {
      title: 'Cần xác nhận phạm vi hồ sơ',
      detail:
        'Hồ sơ đang thiếu các thông tin then chốt. Hãy kết nối với chuyên gia để được hỗ trợ tra cứu và xác định lộ trình chính xác.',
    },
    household: {
      title: 'Hộ kinh doanh chuẩn bị chấm dứt hoạt động',
      detail: 'Cần xác nhận quy trình chấm dứt và nghĩa vụ thuế trước khi đăng ký hộ mới.',
    },
    out_of_scope: {
      title: 'Thủ tục này chưa có danh mục trong bản thử',
      detail:
        'Bản thử hiện chỉ chuẩn bị hồ sơ giải thể hoặc chấm dứt hoạt động. Câu trả lời của bạn được ghi lại để trao đổi với chuyên viên.',
    },
  };
  return headlines[assessment.summary.scope] ?? headlines.needs_confirmation!;
}

export function AssessmentWorkspace({ initial }: { initial: WorkspaceAssessment }) {
  const router = useRouter();
  const [assessment, setAssessment] = useState(initial);
  const [saving, setSaving] = useState('');
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [busy, setBusy] = useState(false);
  // Gợi ý gói chỉ hiện một lần, ngay sau khi khảo sát vừa lưu xong (trang này chỉ dựng ở phía trình duyệt)
  const [plansOpen, setPlansOpen] = useState(() => peekPlanPrompt(initial.id));
  useEffect(() => clearPlanPrompt(initial.id), [initial.id]);

  const status = caseStatus(assessment);
  const inScope = IN_SCOPE.includes(assessment.summary.scope);
  const remaining = assessment.checklist.filter((item) => item.status !== 'available').length;
  const available = assessment.checklist.length - remaining;
  const headline = summaryHeadline(assessment);
  const consultationNotes = [
    `Tóm tắt hồ sơ: ${headline.title}. ${headline.detail}`,
    assessment.summary.scope === 'needs_confirmation' && assessment.summary.unknownFacts.length > 0
      ? `Các thông tin khách hàng chưa rõ cần tra cứu:\n- ${assessment.summary.unknownFacts.join('\n- ')}`
      : '',
    assessment.summary.reviewReasons.length > 0
      ? `Lưu ý chuyên viên:\n- ${assessment.summary.reviewReasons.join('\n- ')}`
      : '',
  ]
    .filter(Boolean)
    .join('\n\n');
  const reached = !inScope ? 1 : status === 'ready' ? 4 : 2;
  const counts = {
    available: assessment.checklist.filter((item) => item.status === 'available').length,
    missing: assessment.checklist.filter((item) => item.status === 'missing').length,
    needsVerification: assessment.checklist.filter((item) => item.status === 'needs_verification')
      .length,
  };

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
            ) : assessment.summary.scope === 'needs_confirmation' ? (
              <>
                <p className="small muted">
                  Chưa tạo checklist tự động · Cần chuyên viên tư vấn xác nhận phạm vi
                </p>
                <Link className="text-link" href={`/chuyen-gia?assessmentId=${assessment.id}`}>
                  Đặt lịch tư vấn ngay <ArrowRight size={14} />
                </Link>
              </>
            ) : (
              <p className="small muted">Chưa áp dụng danh mục cho phạm vi này.</p>
            )}
          </div>
        </div>

        <div id="experts" className="experts-anchor">
          <RecommendedExpertsSection
            key={assessment.id}
            assessmentId={assessment.id}
            initialNotes={consultationNotes}
          />
        </div>

        <div className="case-actions">
          {inScope && (
            <a className="button button-outline" href="#checklist">
              <PencilLine size={16} /> Cập nhật giấy tờ
            </a>
          )}
          <button
            className="button button-outline"
            onClick={() => setPlansOpen(true)}
            type="button"
          >
            <Tags size={16} /> Xem các gói hỗ trợ
          </button>
          <Link className="button button-primary" href={`/ho-so/${assessment.id}/ban-in`}>
            <Download size={16} /> Tải bản tổng hợp
          </Link>
        </div>
        <PlanDialog counts={counts} onOpenChange={setPlansOpen} open={plansOpen} />

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
          ) : assessment.summary.scope === 'needs_confirmation' ? (
            <div className="scope-confirmation-banner" aria-labelledby="scope-confirmation-heading">
              <div className="scope-confirmation-content">
                <CircleAlert className="overview-icon warn" size={24} aria-hidden="true" />
                <div>
                  <h3 id="scope-confirmation-heading">
                    Cần xác nhận phạm vi trước khi lập checklist
                  </h3>
                  <p>
                    Do chưa xác định được tình trạng đăng ký hoặc phát sinh doanh thu, hệ thống chưa
                    thể tạo checklist tự động. Bạn nên trao đổi trực tiếp với chuyên gia để được hỗ
                    trợ kiểm tra mã số thuế và hướng dẫn bước tiếp theo.
                  </p>
                </div>
              </div>
              <Link
                className="button button-primary"
                href={`/chuyen-gia?assessmentId=${assessment.id}`}
              >
                <UserCheck size={16} /> Kết nối chuyên gia để xác định phạm vi
              </Link>
            </div>
          ) : (
            <div className="empty-inline">
              <h3>Hồ sơ chưa có checklist.</h3>
              <p className="small muted">
                Mở khảo sát mới để nhận danh mục phù hợp với nhóm hồ sơ.
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
