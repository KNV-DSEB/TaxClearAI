'use client';

import { Search, SquarePen } from 'lucide-react';
import type { FormEvent } from 'react';

import type { CommunityTopic } from '@/types/community.types';

import styles from './Community.module.css';

export function CommunityFilterBar({
  topics,
  keyword,
  topic,
  onKeywordChange,
  onTopicChange,
  onSearch,
  onAsk,
}: {
  topics: CommunityTopic[];
  keyword: string;
  topic: string;
  onKeywordChange: (value: string) => void;
  onTopicChange: (value: string) => void;
  onSearch: () => void;
  onAsk: () => void;
}) {
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSearch();
  }

  return (
    <form className={styles.filterPanel} onSubmit={submit} role="search">
      <label className={styles.field}>
        <span className={styles.fieldLabel}>Nội dung</span>
        <input
          className={styles.fieldControl}
          type="search"
          name="q"
          autoComplete="off"
          placeholder="Tìm theo nội dung câu hỏi"
          value={keyword}
          onChange={(event) => onKeywordChange(event.target.value)}
        />
      </label>
      <label className={styles.field}>
        <span className={styles.fieldLabel}>Chủ đề</span>
        <select
          className={styles.fieldControl}
          name="topic"
          value={topic}
          onChange={(event) => onTopicChange(event.target.value)}
        >
          <option value="">Tất cả chủ đề</option>
          {topics.map((item) => (
            <option key={item.id} value={item.slug}>
              {item.name}
            </option>
          ))}
        </select>
      </label>
      <button className={`button button-primary ${styles.filterButton}`} type="submit">
        <Search size={16} aria-hidden /> Tìm kiếm
      </button>
      <button
        className={`button button-secondary ${styles.askButton}`}
        type="button"
        onClick={onAsk}
      >
        <SquarePen size={16} aria-hidden /> Đặt câu hỏi
      </button>
    </form>
  );
}
