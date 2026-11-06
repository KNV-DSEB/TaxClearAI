import type { Answers, Question } from '@/types/api.types';

export function isVisible(question: Question, answers: Answers): boolean {
  if (!question.showIf) return true;
  return Object.entries(question.showIf).every(([key, allowed]) =>
    allowed.includes(String(answers[key as keyof Answers])),
  );
}

export function visibleQuestions(questions: Question[], answers: Answers): Question[] {
  return questions.filter((question) => isVisible(question, answers));
}

/** Câu đã bị ẩn thì trả về giá trị mặc định, để đổi loại hình không để lại đáp án cũ. */
export function resetHiddenAnswers(
  answers: Answers,
  questions: Question[],
  defaults: Answers,
): Answers {
  const next = { ...answers };
  for (const question of questions) {
    if (!isVisible(question, next)) Object.assign(next, { [question.id]: defaults[question.id] });
  }
  return next;
}
