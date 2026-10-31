'use client';

import {
  ArrowRight,
  BookOpen,
  Check,
  ClipboardList,
  Copy,
  FileText,
  Info,
  Lightbulb,
  Link2,
  Sparkles,
  Timer,
} from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';

import { ApiError } from '@/services/api.client';
import { chatService } from '@/services/chat.service';
import type { ChatReply, Citation } from '@/types/api.types';

import { AssistantIllustration } from './AssistantIllustration';

const TOPICS = [
  {
    icon: BookOpen,
    label: 'Thủ tục giải thể doanh nghiệp',
    question: 'Thủ tục giải thể doanh nghiệp gồm những bước nào?',
  },
  {
    icon: FileText,
    label: 'Hồ sơ cần chuẩn bị',
    question: 'Hồ sơ giải thể doanh nghiệp gồm những giấy tờ gì?',
  },
  {
    icon: Timer,
    label: 'Thời hạn gửi hồ sơ',
    question:
      'Sau khi có quyết định giải thể, doanh nghiệp phải gửi cho cơ quan đăng ký trong bao lâu?',
  },
  {
    icon: Info,
    label: 'Chấm dứt mã số thuế',
    question: 'Chấm dứt hiệu lực mã số thuế là gì?',
  },
  {
    icon: ClipboardList,
    label: 'Cách dùng checklist',
    question: 'Tôi dùng checklist trên web như thế nào?',
  },
];

// Khớp danh sách tên miền nguồn luật ở backend (modules/chat/legal_sources.py)
const OFFICIAL_DOMAINS = ['chinhphu.vn', 'vbpl.vn', 'gov.vn'];

interface Turn {
  id: number;
  question: string;
  reply?: ChatReply;
  error?: string;
}

function sourceHref(citation: Citation): string | null {
  if (citation.kind === 'product') return citation.url === '/huong-dan' ? citation.url : null;
  try {
    const url = new URL(citation.url);
    const official = OFFICIAL_DOMAINS.some(
      (domain) => url.hostname === domain || url.hostname.endsWith(`.${domain}`),
    );
    return url.protocol === 'https:' && official ? url.href : null;
  } catch {
    return null;
  }
}

function sourceNote(citation: Citation): string {
  if (citation.kind === 'product') return 'Hướng dẫn sử dụng';
  const fetched = citation.fetchedAt
    ? ` lấy ngày ${new Intl.DateTimeFormat('vi-VN').format(new Date(citation.fetchedAt))}`
    : '';
  return citation.reviewStatus === 'unreviewed'
    ? `Trích văn bản gốc${fetched} · chưa được chuyên gia rà soát, chưa xác minh hiệu lực`
    : `Văn bản pháp luật${fetched}`;
}

// Mô hình đôi khi viết danh sách "1. … 2. …" trên một dòng; tách mỗi ý ra dòng riêng
export function formatReply(text: string): string {
  if (!/\s2\.\s/.test(text)) return text;
  return text.replace(/\s+(?=\d{1,2}\.\s)/g, '\n');
}

function Answer({ reply }: { reply: ChatReply }) {
  const [copied, setCopied] = useState(false);
  async function copy(): Promise<void> {
    try {
      await navigator.clipboard.writeText(reply.reply);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }
  return (
    <div className={`answer-card ${reply.disposition === 'answered' ? '' : 'answer-notice'}`}>
      <span className="answer-meta">
        {reply.providerUsed ? 'Gemini · có gọi mô hình' : 'Kiểm tra nội dung · chưa gọi mô hình'}
      </span>
      <p className="answer-text">{formatReply(reply.reply)}</p>
      {reply.citations.length > 0 && (
        <div className="answer-sources">
          <strong>Nguồn tham khảo:</strong>
          {reply.citations.map((citation) => {
            const href = sourceHref(citation);
            return (
              <div className="answer-source" key={citation.sourceId}>
                {href ? (
                  <Link href={href} target="_blank" rel="noopener noreferrer">
                    <Link2 size={14} /> {citation.title}
                  </Link>
                ) : (
                  <span>{citation.title}</span>
                )}
                <span className="small muted">{sourceNote(citation)}</span>
              </div>
            );
          })}
        </div>
      )}
      <div className="answer-actions">
        <button
          className="icon-button"
          aria-label={copied ? 'Đã sao chép câu trả lời' : 'Sao chép câu trả lời'}
          onClick={() => {
            void copy();
          }}
        >
          {copied ? <Check size={16} /> : <Copy size={16} />}
        </button>
      </div>
    </div>
  );
}

export function ChatWorkspace() {
  const router = useRouter();
  const [message, setMessage] = useState('');
  const [accepted, setAccepted] = useState(false);
  const [turns, setTurns] = useState<Turn[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: 'end' });
  }, [turns]);

  function pickTopic(question: string): void {
    setMessage(question);
    setError('');
    inputRef.current?.focus();
  }

  async function submit(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setError('');
    const question = message.trim();
    if (!question) {
      setError('Vui lòng nhập câu hỏi.');
      return;
    }
    if (!accepted) {
      setError('Vui lòng xác nhận chỉ gửi câu hỏi tổng quát hoặc dữ liệu giả định.');
      return;
    }
    const id = Date.now();
    setTurns((current) => [...current, { id, question }]);
    setBusy(true);
    try {
      const reply = await chatService.send(question);
      setTurns((current) => current.map((turn) => (turn.id === id ? { ...turn, reply } : turn)));
      setMessage('');
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        router.replace(`/dang-nhap?returnTo=${encodeURIComponent('/hoi-dap')}`);
        return;
      }
      const text =
        error instanceof Error ? error.message : 'Chưa nhận được phản hồi. Vui lòng thử lại.';
      setTurns((current) =>
        current.map((turn) => (turn.id === id ? { ...turn, error: text } : turn)),
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="chat-layout">
      <aside className="card chat-topics" aria-labelledby="chat-title">
        <h1 id="chat-title">Hỏi đáp cùng AI</h1>
        <p className="muted">Giải thích tổng quát, có trích dẫn văn bản pháp luật.</p>
        <ul aria-label="Chủ đề gợi ý">
          {TOPICS.map(({ icon: Icon, label, question }) => (
            <li key={label}>
              <button
                className={message === question ? 'active' : ''}
                onClick={() => pickTopic(question)}
              >
                <Icon size={16} /> {label}
              </button>
            </li>
          ))}
        </ul>
        <div className="chat-topics-foot">
          <AssistantIllustration />
          <p className="small muted">
            Dùng gói miễn phí của Google Gemini, có giới hạn lượt hỏi mỗi ngày.{' '}
            <a
              href="https://ai.google.dev/gemini-api/terms"
              target="_blank"
              rel="noopener noreferrer"
            >
              Cách Google xử lý nội dung
            </a>
          </p>
        </div>
      </aside>
      <section className="card chat-thread" aria-label="Cuộc hỏi đáp">
        <div className="chat-messages" aria-live="polite">
          {turns.length === 0 && (
            <div className="chat-empty">
              <Sparkles size={26} />
              <p>
                Chọn một chủ đề bên cạnh hoặc gõ câu hỏi của bạn. Mỗi câu hỏi được trả lời độc lập
                và không được lưu lại.
              </p>
            </div>
          )}
          {turns.map((turn) => (
            <div className="chat-turn" key={turn.id}>
              <div className="bubble-user">
                <p>{turn.question}</p>
              </div>
              <div className="bubble-assistant">
                <span className="assistant-mark" aria-hidden="true">
                  <Sparkles size={16} />
                </span>
                {turn.reply ? (
                  <Answer reply={turn.reply} />
                ) : turn.error ? (
                  <p role="alert" className="error-message">
                    {turn.error}
                  </p>
                ) : (
                  <p role="status" className="muted">
                    Đang hỏi trợ lý…
                  </p>
                )}
              </div>
            </div>
          ))}
          <div ref={endRef} />
        </div>
        <form
          className="chat-compose"
          aria-label="Đặt câu hỏi"
          onSubmit={(event) => void submit(event)}
        >
          <div className="chat-input-row">
            <label htmlFor="chat-question" className="sr-only">
              Câu hỏi của bạn
            </label>
            <input
              id="chat-question"
              ref={inputRef}
              value={message}
              maxLength={1500}
              placeholder="Đặt câu hỏi của bạn…"
              onChange={(event) => setMessage(event.target.value)}
              disabled={busy}
              aria-describedby="chat-privacy"
            />
            <button className="send-button" type="submit" disabled={busy} aria-label="Gửi câu hỏi">
              <ArrowRight size={18} />
            </button>
          </div>
          <label className="chat-consent">
            <input
              type="checkbox"
              checked={accepted}
              onChange={(event) => setAccepted(event.target.checked)}
              disabled={busy}
            />
            <span id="chat-privacy">
              Tôi chỉ gửi câu hỏi tổng quát hoặc dữ liệu giả định. Câu hỏi được gửi tới Google để
              trả lời; trợ lý không tính thuế/phạt hay kết luận hồ sơ.
            </span>
          </label>
          {error && (
            <p className="error-message" role="alert">
              {error}
            </p>
          )}
          <p className="chat-tip">
            <Lightbulb size={14} /> Mẹo: hỏi về thủ tục, thời hạn hoặc giấy tờ cần chuẩn bị.
          </p>
        </form>
      </section>
    </div>
  );
}
