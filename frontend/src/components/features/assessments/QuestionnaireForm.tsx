'use client';

import { ArrowLeft, ArrowRight, ClipboardCheck, Lightbulb, ShieldCheck } from 'lucide-react';
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

function SurveyProgress({
  current,
  total,
  percent,
}: {
  current: number;
  total: number;
  percent: number;
}) {
  return (
    <div className="survey-progress">
      <div>
        <span>
          Câu {current} / {total}
        </span>
        <span>{percent}%</span>
      </div>
      <progress className="progress" value={percent} max={100} aria-label="Tiến độ câu hỏi" />
    </div>
  );
}

export function QuestionnaireForm() {
  const router = useRouter();
  const [questionnaire, setQuestionnaire] = useState<Questionnaire | null>(null);
  const [answers, setAnswers] = useState<Answers>(initialAnswers);
  const [step, setStep] = useState(0);
  const [started, setStarted] = useState(false);
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
      <section className="card loading-panel">
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

  const total = questionnaire.questions.length;
  if (!started)
    return (
      <section className="card survey-card survey-welcome" aria-labelledby="welcome-title">
        <SurveyProgress current={1} total={total} percent={0} />
        <span className="welcome-icon">
          <ClipboardCheck size={34} />
        </span>
        <h1 id="welcome-title">
          Chào mừng bạn đến với
          <br />
          khảo sát tình trạng doanh nghiệp
        </h1>
        <p className="survey-lead">
          Bạn sẽ trả lời {total} câu hỏi ngắn. Câu nào chưa rõ, cứ chọn “Chưa biết” — đó là việc
          chuyên viên sẽ giúp xác minh.
        </p>
        <div className="tip-box">
          <Lightbulb size={20} />
          <div>
            <strong>Lưu ý quan trọng</strong>
            <p>
              Kết quả giúp bạn chuẩn bị làm việc với chuyên viên, không thay cho kết luận pháp lý.
              Câu trả lời chỉ được lưu khi bạn chọn “Lưu và xem hồ sơ” ở câu cuối.
            </p>
          </div>
        </div>
        <button className="button button-primary button-large" onClick={() => setStarted(true)}>
          Bắt đầu khảo sát <ArrowRight size={18} />
        </button>
        <p className="survey-foot">
          <ShieldCheck size={15} /> Không nhập tên, mã số thuế, số tài khoản hay tải giấy tờ cá nhân
        </p>
      </section>
    );

  const question = questionnaire.questions[step];
  const last = step === total - 1;
  const value = answers[question.id];
  return (
    <div className="survey-stage">
      <section className="card survey-card" aria-labelledby="question-title">
        <SurveyProgress
          current={step + 1}
          total={total}
          percent={Math.round((step / total) * 100)}
        />
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
        <p className="survey-foot">
          <ShieldCheck size={15} /> Không nhập tên, mã số thuế, số tài khoản hay tải giấy tờ cá nhân
        </p>
      </section>
    </div>
  );
}
