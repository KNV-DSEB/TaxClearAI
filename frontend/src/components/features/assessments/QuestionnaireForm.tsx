'use client';

import { ArrowLeft, ArrowRight, Info } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import { ApiError } from '@/services/api.client';
import { assessmentsService } from '@/services/assessments.service';
import type { Answers, Questionnaire } from '@/types/api.types';

const initialAnswers: Answers = {
  businessType: 'company',
  goal: 'dissolution',
  establishedYear: null,
  revenueStatus: 'unknown',
  revenueStartedYear: null,
  filingStatus: 'unknown',
  recordsStatus: 'unknown',
  taxNoticeStatus: 'unknown',
  laborInsuranceStatus: 'unknown',
  assetsInventoryStatus: 'unknown',
  receivablesPayablesStatus: 'unknown',
};

export function QuestionnaireForm() {
  const router = useRouter();
  const [questionnaire, setQuestionnaire] = useState<Questionnaire | null>(null);
  const [answers, setAnswers] = useState<Answers>(initialAnswers);
  const [step, setStep] = useState(0);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    async function load(): Promise<void> {
      try {
        setQuestionnaire(await assessmentsService.questionnaire(controller.signal));
      } catch (error) {
        if (controller.signal.aborted) return;
        if (error instanceof ApiError && error.status === 401) router.replace('/dang-nhap');
        else setError(error instanceof Error ? error.message : 'Chưa mở được bộ câu hỏi.');
      }
    }
    void load();
    return () => controller.abort();
  }, [router]);

  useEffect(() => {
    function warn(event: BeforeUnloadEvent): void {
      if (dirty) event.preventDefault();
    }
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, [dirty]);

  function answer(value: string): void {
    if (!questionnaire) return;
    const question = questionnaire.questions[step];
    const next = {
      ...answers,
      [question.id]: question.kind === 'year' ? (value ? Number(value) : null) : value,
    };
    if (next.revenueStatus === 'no') next.revenueStartedYear = null;
    setAnswers(next);
    setDirty(true);
    setError('');
  }

  async function submit(): Promise<void> {
    if (!questionnaire) return;
    if (
      answers.establishedYear &&
      answers.revenueStartedYear &&
      answers.revenueStartedYear < answers.establishedYear
    ) {
      setStep(
        questionnaire.questions.findIndex((question) => question.id === 'revenueStartedYear'),
      );
      setError('Năm phát sinh doanh thu không được trước năm thành lập. Vui lòng kiểm tra lại.');
      return;
    }
    setBusy(true);
    setError('');
    try {
      const assessment = await assessmentsService.create(questionnaire.version, answers);
      setDirty(false);
      router.push(`/ho-so/${assessment.id}`);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : 'Chưa lưu được khảo sát. Vui lòng thử lại.',
      );
    } finally {
      setBusy(false);
    }
  }

  if (!questionnaire)
    return (
      <section className="surface loading-panel">
        {error ? (
          <>
            <p role="alert">{error}</p>
            <button className="button button-secondary" onClick={() => window.location.reload()}>
              Mở lại bộ câu hỏi
            </button>
          </>
        ) : (
          <p role="status">Đang mở bộ câu hỏi…</p>
        )}
      </section>
    );

  const question = questionnaire.questions[step];
  const last = step === questionnaire.questions.length - 1;
  const value = answers[question.id];
  return (
    <div className="survey-layout">
      <aside className="survey-intro">
        <span className="section-kicker">Chuẩn bị khảo sát</span>
        <h1>
          Bắt đầu từ điều
          <br />
          bạn biết.
        </h1>
        <p>
          Không cần tìm đủ giấy tờ ngay. Câu trả lời “Chưa biết” giúp ghi nhận việc cần chuyên viên
          xác minh.
        </p>
        <ol className="survey-outline">
          <li className="current">Ghi nhận tình trạng</li>
          <li>Xem danh mục hồ sơ</li>
          <li>Lưu và bổ sung sau</li>
        </ol>
        <p className="small muted">Thông tin được lưu khi bạn chọn “Lưu và xem hồ sơ”.</p>
      </aside>
      <section className="surface question-panel" aria-labelledby="question-title">
        <div className="question-progress">
          <span>
            Câu {step + 1} / {questionnaire.questions.length}
          </span>
          <span>Khảo sát doanh nghiệp</span>
        </div>
        <progress
          className="progress"
          value={step + 1}
          max={questionnaire.questions.length}
          aria-label="Tiến độ câu hỏi"
        />
        <p className="draft-note">
          <Info size={16} /> Nội dung mẫu · Chờ cố vấn xác nhận
        </p>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            if (last) void submit();
            else setStep(step + 1);
          }}
        >
          <h2 id="question-title" tabIndex={-1}>
            {question.label}
          </h2>
          <p className="question-help">Chọn thông tin gần với tình trạng thực tế bạn đang biết.</p>
          <fieldset key={question.id} disabled={busy}>
            <legend className="sr-only">{question.label}</legend>
            {question.kind === 'choice' ? (
              question.options.map((option) => (
                <label
                  className={`answer-option ${value === option.value ? 'selected' : ''}`}
                  key={option.value}
                >
                  <input
                    type="radio"
                    name={question.id}
                    value={option.value}
                    checked={value === option.value}
                    onChange={(event) => answer(event.target.value)}
                  />
                  <span>{option.label}</span>
                </label>
              ))
            ) : (
              <div className="year-field">
                <label htmlFor={question.id}>Năm (để trống nếu chưa biết hoặc không áp dụng)</label>
                <input
                  id={question.id}
                  type="number"
                  name={question.id}
                  inputMode="numeric"
                  min={1900}
                  max={new Date().getFullYear()}
                  value={value === null ? '' : String(value)}
                  onChange={(event) => answer(event.target.value)}
                  disabled={question.id === 'revenueStartedYear' && answers.revenueStatus === 'no'}
                  placeholder="Ví dụ: 2015"
                />
              </div>
            )}
          </fieldset>
          {error && (
            <p className="error-message" role="alert">
              {error}
            </p>
          )}
          <div className="question-actions">
            <button
              className="button button-quiet"
              type="button"
              onClick={() => setStep(step - 1)}
              disabled={step === 0 || busy}
            >
              <ArrowLeft size={17} /> Quay lại
            </button>
            <button className="button button-primary" disabled={busy} type="submit">
              {busy ? 'Đang lưu…' : last ? 'Lưu và xem hồ sơ' : 'Câu tiếp theo'}
              {!busy && <ArrowRight size={17} />}
            </button>
          </div>
        </form>
        <p className="question-privacy">
          Không nhập tên, mã số thuế, số tài khoản hoặc tải giấy tờ cá nhân.
        </p>
      </section>
    </div>
  );
}
