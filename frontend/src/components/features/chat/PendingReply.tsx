'use client';

import { useEffect, useState } from 'react';

// Thời gian thật của backend: thường 2–5 giây, thử lại tối đa 3 lần, dừng sau 22 giây
const STAGES = [
  { after: 0, text: 'Đang tìm nguồn phù hợp…' },
  { after: 3000, text: 'Trợ lý đang soạn câu trả lời…' },
  { after: 8000, text: 'Hơi lâu hơn thường lệ, trợ lý đang thử lại. Có thể mất tới 20 giây.' },
];

export function PendingReply() {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const started = Date.now();
    const timer = window.setInterval(() => setElapsed(Date.now() - started), 500);
    return () => window.clearInterval(timer);
  }, []);

  const stage = [...STAGES].reverse().find((item) => elapsed >= item.after) ?? STAGES[0];
  return (
    <p role="status" className="chat-pending">
      <span className="chat-dots" aria-hidden="true">
        <i />
        <i />
        <i />
      </span>
      {stage.text}
    </p>
  );
}
