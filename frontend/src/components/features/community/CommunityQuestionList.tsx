'use client';

import { ChevronDown, ChevronUp, MessageCircle } from 'lucide-react';
import { useState } from 'react';

import type { CommunityQuestion } from '@/types/community.types';

import styles from './Community.module.css';

const dateFormatter = new Intl.DateTimeFormat('vi-VN', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
});

function initials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(-2)
    .map((part) => part[0])
    .join('')
    .toLocaleUpperCase('vi-VN');
}

export function CommunityQuestionList({ items }: { items: CommunityQuestion[] }) {
  const [expanded, setExpanded] = useState<Set<string>>(() => new Set());

  function toggle(id: string) {
    setExpanded((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  if (items.length === 0) {
    return (
      <div className={styles.emptyState}>
        <h2 className={styles.emptyTitle}>Chưa có tình huống phù hợp</h2>
        <p>Thử đổi từ khóa hoặc chọn một chủ đề khác để xem thêm câu hỏi.</p>
      </div>
    );
  }

  return (
    <ul className={styles.questionList} aria-label="Danh sách hỏi đáp cộng đồng">
      {items.map((item) => {
        const isExpanded = expanded.has(item.id);
        const answerId = `answer-${item.id}`;
        return (
          <li className={styles.questionCard} key={item.id}>
            <div className={styles.questionTopline}>
              <span className={styles.avatar} aria-hidden="true">
                {initials(item.authorName) || 'ẨD'}
              </span>
              <div className={styles.authorBlock}>
                <p className={styles.authorName}>{item.authorName}</p>
                <time className={styles.dateLine} dateTime={item.createdAt}>
                  Đăng ngày {dateFormatter.format(new Date(item.createdAt))}
                </time>
              </div>
              <span className={styles.topicTag}>{item.topic.name}</span>
            </div>
            <div className={styles.questionBody}>
              <h2 className={styles.questionTitle}>{item.title}</h2>
              <p className={styles.questionText}>
                <span className={styles.questionLabel}>Hỏi</span>
                {item.questionContent}
              </p>
              <button
                className={styles.answerToggle}
                type="button"
                aria-expanded={isExpanded}
                aria-controls={answerId}
                onClick={() => toggle(item.id)}
              >
                <MessageCircle size={16} aria-hidden />
                {item.answerContent ? (isExpanded ? 'Thu gọn câu trả lời' : 'Xem câu trả lời') : 'Chưa có câu trả lời'}
                {item.answerContent &&
                  (isExpanded ? <ChevronUp size={16} aria-hidden /> : <ChevronDown size={16} aria-hidden />)}
              </button>
            </div>
            <div
              className={`${styles.answerPanel} ${isExpanded ? styles.answerPanelOpen : ''}`}
              id={answerId}
              aria-hidden={!isExpanded}
            >
              <div className={styles.answerInner}>
                {item.answerContent ? (
                  <div className={styles.answerContent}>
                    <span className={styles.answerLabel}>Trả lời</span>
                    {item.answerContent}
                    {item.answeredBy && <span className={styles.answerByline}>{item.answeredBy}</span>}
                  </div>
                ) : (
                  <p className={styles.pendingAnswer}>Câu hỏi đang chờ cộng đồng phản hồi.</p>
                )}
              </div>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
