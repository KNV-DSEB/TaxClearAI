'use client';

import { ArrowUpRight, MessageCircle, Send } from 'lucide-react';
import Link from 'next/link';
import { useState } from 'react';

import { chatService } from '@/services/chat.service';
import type { ChatReply, Citation } from '@/types/api.types';

// Khớp danh sách tên miền nguồn luật ở backend (modules/chat/legal_sources.py)
const OFFICIAL_DOMAINS = ['chinhphu.vn', 'vbpl.vn', 'gov.vn'];

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

export function ChatPanel() {
  const [message, setMessage] = useState('');
  const [accepted, setAccepted] = useState(false);
  const [reply, setReply] = useState<ChatReply | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function submit(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setError('');
    if (!accepted) {
      setError('Vui lòng xác nhận chỉ gửi câu hỏi tổng quát hoặc dữ liệu giả định.');
      return;
    }
    if (!message.trim()) {
      setError('Vui lòng nhập câu hỏi.');
      return;
    }
    setBusy(true);
    try {
      setReply(await chatService.send(message.trim()));
    } catch (error) {
      setError(
        error instanceof Error ? error.message : 'Chưa nhận được phản hồi. Vui lòng thử lại.',
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="surface chat-panel" aria-labelledby="chat-heading">
      <div className="chat-heading">
        <MessageCircle size={21} />
        <h2 id="chat-heading">Hỏi trợ lý</h2>
        <span>Gemini</span>
      </div>
      <p className="small muted">
        Hỏi cách dùng checklist, hoặc hỏi về thủ tục giải thể và chấm dứt mã số thuế.
      </p>
      <form
        aria-label="Đặt câu hỏi"
        onSubmit={(event) => {
          void submit(event);
        }}
      >
        <label htmlFor="chat-question" className="chat-input-label">
          Câu hỏi của bạn
        </label>
        <textarea
          id="chat-question"
          name="message"
          rows={3}
          maxLength={1500}
          required
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Ví dụ: Hồ sơ giải thể doanh nghiệp gồm những giấy tờ gì?"
          aria-describedby="chat-privacy"
          disabled={busy}
        />
        <p id="chat-privacy" className="chat-privacy">
          Câu hỏi được gửi tới Google để trả lời. Không tự gửi hồ sơ đã lưu. Mỗi câu hỏi độc lập;
          hội thoại không được lưu.
        </p>
        <label className="chat-consent">
          <input
            name="disclosureAccepted"
            type="checkbox"
            checked={accepted}
            onChange={(event) => setAccepted(event.target.checked)}
            required
            disabled={busy}
          />
          <span>
            Tôi chỉ gửi câu hỏi tổng quát hoặc dữ liệu giả định, không có thông tin riêng tư.
          </span>
        </label>
        <button className="button button-primary" disabled={busy} type="submit">
          {busy ? 'Đang hỏi trợ lý…' : 'Gửi câu hỏi'}
          <Send size={15} />
        </button>
      </form>
      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}
      {reply && (
        <div className="chat-answer" aria-live="polite">
          <span className="chat-answer-label">
            {reply.providerUsed
              ? 'Gemini · Có gọi mô hình'
              : 'Kiểm tra nội dung · Chưa gọi mô hình'}
          </span>
          <p>{reply.reply}</p>
          {reply.citations.map((citation) => {
            const href = sourceHref(citation);
            return (
              <div className="chat-source" key={citation.sourceId}>
                {href ? (
                  <Link href={href} target="_blank" rel="noopener noreferrer">
                    {citation.title}
                    <ArrowUpRight size={13} />
                  </Link>
                ) : (
                  <span>Không mở được đường dẫn nguồn.</span>
                )}
                <span>{sourceNote(citation)}</span>
              </div>
            );
          })}
        </div>
      )}
      <p className="small muted chat-footnote">
        Không tính thuế/phạt hay thay chuyên viên kết luận hồ sơ. Gói miễn phí có hạn mức.{' '}
        <a href="https://ai.google.dev/gemini-api/terms" target="_blank" rel="noopener noreferrer">
          Cách Google xử lý nội dung
        </a>
      </p>
    </section>
  );
}
