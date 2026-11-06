const KEY = 'tax-clear:plan-prompt';

// sessionStorage có thể bị chặn (chế độ riêng tư); lời gợi ý gói là tùy chọn nên bỏ qua im lặng là chấp nhận được

/** Đánh dấu hồ sơ vừa tạo xong để trang hồ sơ hiện gợi ý gói đúng một lần. */
export function markPlanPrompt(caseId: string): void {
  try {
    sessionStorage.setItem(KEY, caseId);
  } catch {
    // Không lưu được thì không hiện gợi ý
  }
}

/** Hồ sơ này vừa được tạo xong và chưa hiện gợi ý gói? */
export function peekPlanPrompt(caseId: string): boolean {
  try {
    return sessionStorage.getItem(KEY) === caseId;
  } catch {
    return false;
  }
}

/** Xóa dấu sau khi đã hiện, để tải lại trang không hiện lại. */
export function clearPlanPrompt(caseId: string): void {
  try {
    if (sessionStorage.getItem(KEY) === caseId) sessionStorage.removeItem(KEY);
  } catch {
    // Không xóa được thì cùng lắm hiện thêm một lần
  }
}
