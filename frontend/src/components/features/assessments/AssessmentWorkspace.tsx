'use client';

import { Check, ClipboardList, Info, LogOut, Plus, Trash2 } from 'lucide-react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { assessmentsService } from '@/services/assessments.service';
import { authService } from '@/services/auth.service';
import type { Assessment, ItemStatus } from '@/types/api.types';

type WorkspaceAssessment = Omit<Assessment, 'answers'>;

const ChatPanel = dynamic(() => import('../chat/ChatPanel').then((module) => module.ChatPanel), {
  loading: () => (
    <p role="status" className="surface summary-panel">
      Đang mở trợ lý…
    </p>
  ),
});

export function AssessmentWorkspace({ initial }: { initial: WorkspaceAssessment }) {
  const router = useRouter();
  const [assessment, setAssessment] = useState(initial);
  const [saving, setSaving] = useState('');
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [busy, setBusy] = useState(false);
  const available = assessment.checklist.filter((item) => item.status === 'available').length;

  async function update(itemId: string, status: ItemStatus): Promise<void> {
    setSaving(itemId);
    setNotice('');
    setError('');
    try {
      const updated = await assessmentsService.updateItem(assessment.id, itemId, status);
      setAssessment((current) => ({
        ...current,
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
      router.replace('/khao-sat');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Chưa xóa được. Vui lòng thử lại.');
    } finally {
      setBusy(false);
    }
  }

  async function logout(): Promise<void> {
    try {
      await authService.logout();
      router.replace('/dang-nhap');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Chưa đăng xuất được. Vui lòng thử lại.');
    }
  }

  return (
    <>
      <div className="workspace-heading">
        <div>
          <span className="section-kicker">Hồ sơ chuẩn bị khảo sát</span>
          <h1>Đã rõ hơn. Cùng bổ sung từng mục.</h1>
          <p className="muted">Giữ lại đường dẫn trang này để mở lại hồ sơ sau khi đăng nhập.</p>
        </div>
        <button
          className="button button-quiet"
          onClick={() => {
            void logout();
          }}
        >
          <LogOut size={16} /> Đăng xuất
        </button>
      </div>
      <aside className="disclosure compact">
        <Info size={19} />
        <p>{assessment.summary.notice}</p>
      </aside>
      <div className="workspace-grid">
        <section className="surface checklist-panel">
          <div className="panel-heading">
            <div>
              <ClipboardList size={23} />
              <h2>Danh mục chuẩn bị</h2>
            </div>
            <span>
              {available} / {assessment.checklist.length} đã có
            </span>
          </div>
          {assessment.checklist.length > 0 ? (
            <>
              <p className="muted small">
                Danh mục gợi ý để khảo sát, chưa xác nhận là giấy tờ bắt buộc cho trường hợp của
                bạn.
              </p>
              <progress
                className="progress"
                aria-label="Giấy tờ đã có"
                value={available}
                max={assessment.checklist.length}
              />
              <ul className="checklist">
                {assessment.checklist.map((item) => (
                  <li key={item.id}>
                    <span
                      className={`check-indicator ${item.status === 'available' ? 'done' : ''}`}
                      aria-hidden="true"
                    >
                      {item.status === 'available' ? <Check size={15} /> : null}
                    </span>
                    <div className="checklist-copy">
                      <strong>{item.label}</strong>
                      <span>Chờ cố vấn xác nhận</span>
                    </div>
                    <select
                      name={item.code}
                      aria-label={`Trạng thái: ${item.label}`}
                      value={item.status}
                      disabled={saving !== '' || busy}
                      onChange={(event) => {
                        void update(item.id, event.target.value as ItemStatus);
                      }}
                    >
                      <option value="needs_verification">Cần xác minh</option>
                      <option value="available">Đã có</option>
                      <option value="missing">Còn thiếu</option>
                    </select>
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <div className="empty-state">
              <h3>Cần xác nhận phạm vi trước.</h3>
              <p>
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
        <aside className="workspace-sidebar">
          <ChatPanel />
          <section className="surface summary-panel">
            <h2>Những điều cần làm rõ</h2>
            {assessment.summary.reviewReasons.length > 0 ? (
              <ul className="review-list">
                {assessment.summary.reviewReasons.map((text) => (
                  <li key={text}>{text}</li>
                ))}
              </ul>
            ) : (
              <p className="muted">
                Chuyên viên vẫn cần rà soát câu trả lời trước khi áp dụng cho hồ sơ thật.
              </p>
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
          <section className="next-step-panel">
            <h2>Bước tiếp theo của bạn</h2>
            <p>
              Tìm lại các giấy tờ đang có và cập nhật trạng thái. Sau đó trao đổi bản tổng hợp này
              với chuyên viên để xác minh.
            </p>
            <p className="small">Không cần nhập số thuế hay gửi chứng từ lên bản thử.</p>
          </section>
          <section className="surface summary-panel">
            <h2>Quản lý hồ sơ thử</h2>
            <p className="small muted">
              Lưu đến{' '}
              {new Intl.DateTimeFormat('vi-VN', { dateStyle: 'medium' }).format(
                new Date(assessment.expiresAt),
              )}
              . Chỉ sử dụng dữ liệu giả định.
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
        </aside>
      </div>
    </>
  );
}
