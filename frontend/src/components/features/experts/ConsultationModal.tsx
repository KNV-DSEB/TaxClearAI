'use client';

import * as Dialog from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { useEffect, useState, type FormEvent } from 'react';

import { SCOPE_TITLES } from '@/components/features/assessments/case-status';
import { assessmentsService } from '@/services/assessments.service';
import { expertsService } from '@/services/experts.service';
import type { Assessment } from '@/types/api.types';
import type { ConsultationFormValues, ConsultationResponse, Expert } from '@/types/experts.types';

import styles from './Experts.module.css';

export function ConsultationModal({
  expert,
  assessmentId,
  initialNotes,
  open,
  onOpenChange,
}: {
  expert: Expert;
  assessmentId?: string;
  initialNotes?: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [values, setValues] = useState<ConsultationFormValues>({
    expertId: expert.id,
    assessmentId,
    contactName: '',
    contactPhone: '',
    contactEmail: '',
    businessType: '',
    serviceNeeded: '',
    shareDataConsent: false,
    sampleAcknowledged: false,
    consultationMethod: 'online',
    notes: initialNotes ?? '',
  });
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<ConsultationResponse | null>(null);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [assessmentLoading, setAssessmentLoading] = useState(Boolean(assessmentId));
  const [assessmentError, setAssessmentError] = useState('');

  useEffect(() => {
    if (!assessmentId) return;
    const controller = new AbortController();
    assessmentsService
      .get(assessmentId, controller.signal)
      .then(setAssessment)
      .catch((loadError: unknown) => {
        if (!controller.signal.aborted) {
          setAssessmentError(
            loadError instanceof Error ? loadError.message : 'Không tải được tóm tắt hồ sơ.',
          );
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setAssessmentLoading(false);
      });
    return () => controller.abort();
  }, [assessmentId]);

  function update<K extends keyof ConsultationFormValues>(
    key: K,
    value: ConsultationFormValues[K],
  ) {
    setValues((current) => ({ ...current, [key]: value }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    if (!values.sampleAcknowledged) {
      setError('Vui lòng xác nhận đây là bản thử và chỉ nhập thông tin giả định.');
      return;
    }
    setSending(true);
    try {
      const payload: ConsultationFormValues = {
        ...values,
        contactName: values.contactName.trim(),
        contactPhone: values.contactPhone.trim(),
        contactEmail: values.contactEmail?.trim() || undefined,
        businessType: values.businessType?.trim() || undefined,
        notes: values.notes.trim(),
      };
      setResult(await expertsService.submitConsultation(payload));
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : 'Chưa gửi được yêu cầu. Vui lòng thử lại.',
      );
    } finally {
      setSending(false);
    }
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className={styles.overlay} />
        <Dialog.Content className={styles.modal}>
          <Dialog.Close className={`icon-button ${styles.closeButton}`} aria-label="Đóng cửa sổ">
            <X size={16} aria-hidden />
          </Dialog.Close>
          <div className={styles.modalHeader}>
            <span className={styles.avatar} aria-hidden="true">
              {expert.fullName.slice(0, 1)}
            </span>
            <div>
              <Dialog.Title className={styles.modalTitle}>Đặt lịch tư vấn</Dialog.Title>
              <Dialog.Description className={styles.modalDescription}>
                {expert.fullName} · {expert.title}
              </Dialog.Description>
            </div>
          </div>

          <div className={styles.modalFeeNotice}>
            <span>Chi phí tư vấn tham khảo:</span>
            <strong>{expert.consultationFeeText}</strong>
            <p className="small muted">
              Mức phí chính xác sẽ được đối tác xác nhận sau khi thẩm định dữ liệu hồ sơ và khối
              lượng chứng từ thực tế.
            </p>
          </div>

          {result ? (
            <div className={styles.form}>
              <p className={styles.successMessage} role="status">
                Tax Clear đã nhận yêu cầu tư vấn. Yêu cầu đang chờ tiếp nhận.
              </p>
              <div className={`${styles.formActions} ${styles.fullWidth}`}>
                <button
                  className="button button-primary"
                  type="button"
                  onClick={() => onOpenChange(false)}
                >
                  Hoàn tất
                </button>
              </div>
            </div>
          ) : (
            <form className={styles.form} onSubmit={submit}>
              <label className={styles.field}>
                <span className={styles.fieldLabel}>Họ tên</span>
                <input
                  className={styles.fieldControl}
                  name="contactName"
                  autoComplete="name"
                  required
                  maxLength={150}
                  value={values.contactName}
                  onChange={(event) => update('contactName', event.target.value)}
                />
              </label>
              <label className={`${styles.field} ${styles.fullWidth}`}>
                <span className={styles.fieldLabel}>Dịch vụ cần thực hiện</span>
                <select
                  className={styles.fieldControl}
                  name="serviceNeeded"
                  value={values.serviceNeeded}
                  onChange={(event) => update('serviceNeeded', event.target.value)}
                >
                  <option value="">Chọn dịch vụ nếu đã xác định</option>
                  <option value="Dọn dẹp và hoàn thiện sổ sách kế toán">
                    Dọn dẹp và hoàn thiện sổ sách kế toán
                  </option>
                  <option value="Lập báo cáo tài chính và quyết toán thuế giải thể">
                    Lập báo cáo tài chính và quyết toán thuế giải thể
                  </option>
                  <option value="Đóng mã số thuế và giải thể trọn gói">
                    Đóng mã số thuế và giải thể trọn gói
                  </option>
                  <option value="Kiểm tra và giải trình chênh lệch số liệu thuế">
                    Kiểm tra và giải trình chênh lệch số liệu thuế
                  </option>
                  <option value="Khác">Khác</option>
                </select>
              </label>
              {assessmentId && (
                <section
                  className={`${styles.caseSummary} ${styles.fullWidth}`}
                  aria-label="Tóm tắt dữ liệu hồ sơ"
                >
                  <div className={styles.caseSummaryHeader}>
                    <div>
                      <span className={styles.caseEyebrow}>Hồ sơ được chuyển giao</span>
                      <h3>
                        {assessment
                          ? SCOPE_TITLES[assessment.summary.scope]
                          : 'Tóm tắt hồ sơ khảo sát'}
                      </h3>
                    </div>
                    {assessment && (
                      <span className={styles.caseCount}>
                        {assessment.checklist.length} mục giấy tờ
                      </span>
                    )}
                  </div>
                  {assessmentLoading ? (
                    <p className={styles.caseHint} role="status">
                      Đang tải checklist…
                    </p>
                  ) : assessmentError ? (
                    <p className={styles.caseError} role="alert">
                      {assessmentError}
                    </p>
                  ) : assessment ? (
                    <>
                      <div className={styles.caseStats}>
                        <span>
                          {
                            assessment.checklist.filter((item) => item.status === 'available')
                              .length
                          }{' '}
                          mục đã chuẩn bị
                        </span>
                        <span>
                          {
                            assessment.checklist.filter((item) => item.status !== 'available')
                              .length
                          }{' '}
                          vấn đề cần làm rõ
                        </span>
                      </div>
                      <ul className={styles.caseChecklist}>
                        {assessment.checklist.slice(0, 5).map((item) => (
                          <li key={item.id}>
                            <span>{item.label}</span>
                            <strong>
                              {item.status === 'available'
                                ? 'Đã có'
                                : item.status === 'missing'
                                  ? 'Còn thiếu'
                                  : 'Cần xác minh'}
                            </strong>
                          </li>
                        ))}
                        {assessment.checklist.length > 5 && (
                          <li className={styles.caseHint}>
                            Còn {assessment.checklist.length - 5} mục khác trong snapshot.
                          </li>
                        )}
                      </ul>
                    </>
                  ) : (
                    <p className={styles.caseHint}>Không có dữ liệu hồ sơ để đính kèm.</p>
                  )}
                  <label className={styles.consentOption}>
                    <input
                      type="checkbox"
                      name="shareDataConsent"
                      checked={values.shareDataConsent}
                      onChange={(event) => update('shareDataConsent', event.target.checked)}
                    />
                    <span>
                      Cho phép đối tác xem câu trả lời khảo sát và checklist để thẩm định, báo giá
                      chính xác.
                    </span>
                  </label>
                </section>
              )}
              <p className={styles.caseHint} role="note">
                Bản thử nghiệm: các đối tác là hồ sơ minh họa, yêu cầu chưa được chuyển cho chuyên
                gia thật. Chỉ nhập thông tin giả định.
              </p>
              <label className={styles.consentOption}>
                <input
                  type="checkbox"
                  name="sampleAcknowledged"
                  required
                  checked={values.sampleAcknowledged}
                  onChange={(event) => update('sampleAcknowledged', event.target.checked)}
                />
                <span>Tôi hiểu đây là bản thử và chỉ nhập thông tin giả định.</span>
              </label>
              <label className={styles.field}>
                <span className={styles.fieldLabel}>Số điện thoại</span>
                <input
                  className={styles.fieldControl}
                  type="tel"
                  name="contactPhone"
                  autoComplete="tel"
                  inputMode="tel"
                  minLength={8}
                  maxLength={50}
                  required
                  value={values.contactPhone}
                  onChange={(event) => update('contactPhone', event.target.value)}
                />
              </label>
              <label className={styles.field}>
                <span className={styles.fieldLabel}>
                  Email <span className="muted">(không bắt buộc)</span>
                </span>
                <input
                  className={styles.fieldControl}
                  type="email"
                  name="contactEmail"
                  autoComplete="email"
                  maxLength={150}
                  value={values.contactEmail}
                  onChange={(event) => update('contactEmail', event.target.value)}
                />
              </label>
              <label className={styles.field}>
                <span className={styles.fieldLabel}>Loại hình</span>
                <select
                  className={styles.fieldControl}
                  name="businessType"
                  value={values.businessType}
                  onChange={(event) => update('businessType', event.target.value)}
                >
                  <option value="">Chọn nếu phù hợp</option>
                  <option value="Doanh nghiệp">Doanh nghiệp</option>
                  <option value="Hộ kinh doanh">Hộ kinh doanh</option>
                </select>
              </label>
              <fieldset className={`${styles.field} ${styles.fullWidth}`}>
                <legend className={styles.fieldLabel}>Hình thức tư vấn</legend>
                <div className={styles.methodGroup}>
                  <label className={styles.methodOption}>
                    <input
                      type="radio"
                      name="consultationMethod"
                      value="online"
                      checked={values.consultationMethod === 'online'}
                      onChange={() => update('consultationMethod', 'online')}
                    />
                    <span>
                      <span className={styles.methodTitle}>Online</span>
                      <span className={styles.methodText}>Google Meet hoặc Zalo</span>
                    </span>
                  </label>
                  <label className={styles.methodOption}>
                    <input
                      type="radio"
                      name="consultationMethod"
                      value="in_person"
                      checked={values.consultationMethod === 'in_person'}
                      onChange={() => update('consultationMethod', 'in_person')}
                    />
                    <span>
                      <span className={styles.methodTitle}>Gặp trực tiếp</span>
                      <span className={styles.methodText}>
                        Thống nhất địa điểm sau khi tiếp nhận
                      </span>
                    </span>
                  </label>
                </div>
              </fieldset>
              <label className={`${styles.field} ${styles.fullWidth}`}>
                <span className={styles.fieldLabel}>Vấn đề cần hỗ trợ</span>
                <textarea
                  className={`${styles.fieldControl} ${styles.textArea}`}
                  name="notes"
                  required
                  minLength={1}
                  maxLength={5000}
                  value={values.notes}
                  onChange={(event) => update('notes', event.target.value)}
                  placeholder="Mô tả ngắn tình huống và điều bạn cần tư vấn…"
                />
                <span className={styles.hint}>
                  Không nhập mã số thuế hoặc giấy tờ tùy thân nếu chưa cần thiết.
                </span>
              </label>
              {error && (
                <p className={styles.errorMessage} role="alert">
                  {error}
                </p>
              )}
              <div className={`${styles.formActions} ${styles.fullWidth}`}>
                <button
                  className="button button-quiet"
                  type="button"
                  onClick={() => onOpenChange(false)}
                  disabled={sending}
                >
                  Để sau
                </button>
                <button className="button button-primary" type="submit" disabled={sending}>
                  {sending ? 'Đang gửi…' : 'Gửi yêu cầu'}
                </button>
              </div>
            </form>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
