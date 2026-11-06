import type { Assessment, CaseStatus } from '@/types/api.types';

export const SCOPE_TITLES: Record<Assessment['summary']['scope'], string> = {
  a1: 'Hộ kinh doanh chưa đăng ký',
  a2: 'Hộ kinh doanh cần hoàn tất kê khai',
  a3: 'Hộ kinh doanh cần rà soát kê khai',
  b1: 'Doanh nghiệp chưa phát sinh doanh số',
  b2: 'Giải thể doanh nghiệp',
  household: 'Chấm dứt hoạt động hộ kinh doanh',
  needs_confirmation: 'Cần xác nhận phạm vi',
  out_of_scope: 'Ngoài phạm vi bản thử',
};

// Phạm vi có danh mục giấy tờ; khớp backend (content.IN_SCOPE)
export const IN_SCOPE: string[] = ['a1', 'a2', 'a3', 'b1', 'b2', 'household'];

// "Đủ giấy tờ" là đủ để làm việc với chuyên viên, không phải đã hoàn tất thủ tục pháp lý
export const STATUS_LABELS: Record<CaseStatus, string> = {
  in_progress: 'Đang thực hiện',
  ready: 'Đã đủ giấy tờ',
  expired: 'Đã hết hạn',
};

export function caseStatus(
  assessment: Pick<Assessment, 'checklist' | 'expiresAt' | 'summary'>,
): CaseStatus {
  if (new Date(assessment.expiresAt).getTime() <= Date.now()) return 'expired';
  const { checklist, summary } = assessment;
  const ready =
    IN_SCOPE.includes(summary.scope) &&
    checklist.length > 0 &&
    checklist.every((item) => item.status === 'available');
  return ready ? 'ready' : 'in_progress';
}

export function formatDate(value: string, withTime = false): string {
  return new Intl.DateTimeFormat('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    ...(withTime ? { hour: '2-digit', minute: '2-digit' } : {}),
  }).format(new Date(value));
}
