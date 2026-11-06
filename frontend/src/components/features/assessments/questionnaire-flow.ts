import type { Answers, Question } from '@/types/api.types';

// Cùng quy tắc với backend: ô tự điền không nhận email, số điện thoại hay dãy số dài như mã số thuế
const IDENTIFIER = /[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|(?:\d[\s.-]*){7,}/;

export function isVisible(question: Question, answers: Answers): boolean {
  if (!question.showIf) return true;
  return Object.entries(question.showIf).every(([key, allowed]) =>
    allowed.includes(String(answers[key])),
  );
}

export function visibleQuestions(questions: Question[], answers: Answers): Question[] {
  return questions.filter((question) => isVisible(question, answers));
}

/** Câu đã bị ẩn thì xóa đáp án, để đổi loại hình không để lại đáp án cũ. */
export function resetHiddenAnswers(answers: Answers, questions: Question[]): Answers {
  const next = { ...answers };
  for (const question of questions) {
    if (!isVisible(question, next)) next[question.id] = null;
  }
  return next;
}

export function isAnswered(value: string | number | null | undefined): boolean {
  return value !== null && value !== undefined && value !== '';
}

/** Trả thông báo lỗi tiếng Việt nếu đáp án của câu này chưa hợp lệ, ngược lại trả chuỗi rỗng. */
export function answerProblem(
  question: Question,
  value: string | number | null | undefined,
): string {
  if (!isAnswered(value)) {
    return question.required ? 'Vui lòng trả lời câu này để đi tiếp.' : '';
  }
  if (question.kind === 'text' && IDENTIFIER.test(String(value))) {
    return 'Vui lòng không nhập email, số điện thoại hay mã số thuế.';
  }
  if (question.kind === 'year') {
    const year = Number(value);
    if (!Number.isInteger(year) || year < 1900 || year > new Date().getFullYear()) {
      return `Năm cần nằm trong khoảng 1900 đến ${new Date().getFullYear()}.`;
    }
  }
  if (question.kind === 'number' && !(Number(value) >= 0)) {
    return 'Vui lòng nhập một số không âm.';
  }
  return '';
}
