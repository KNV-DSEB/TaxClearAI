'use client';

import * as Dialog from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { useState, type FormEvent } from 'react';

import { communityService } from '@/services/community.service';
import type { CommunityTopic, CreateCommunityQuestion } from '@/types/community.types';

import styles from './Community.module.css';

export function AskQuestionModal({
  open,
  topics,
  onOpenChange,
  onCreated,
}: {
  open: boolean;
  topics: CommunityTopic[];
  onOpenChange: (open: boolean) => void;
  onCreated: () => void;
}) {
  const [topicSlug, setTopicSlug] = useState('');
  const [authorName, setAuthorName] = useState('');
  const [title, setTitle] = useState('');
  const [questionContent, setQuestionContent] = useState('');
  const [error, setError] = useState('');
  const [sending, setSending] = useState(false);

  function changeOpen(nextOpen: boolean) {
    if (nextOpen) setError('');
    onOpenChange(nextOpen);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setSending(true);
    const data: CreateCommunityQuestion = {
      topicSlug: topicSlug || topics[0]?.slug || '',
      ...(authorName.trim() ? { authorName: authorName.trim() } : {}),
      title: title.trim(),
      questionContent: questionContent.trim(),
    };
    try {
      await communityService.createQuestion(data);
      onOpenChange(false);
      setTitle('');
      setQuestionContent('');
      setAuthorName('');
      onCreated();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Chưa gửi được câu hỏi. Vui lòng thử lại.');
    } finally {
      setSending(false);
    }
  }

  return (
    <Dialog.Root open={open} onOpenChange={changeOpen}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/50" />
        <Dialog.Content className={styles.modalContent}>
          <Dialog.Close className="icon-button absolute right-4 top-4" aria-label="Đóng cửa sổ">
            <X size={16} aria-hidden />
          </Dialog.Close>
          <Dialog.Title className={styles.modalTitle}>Đặt câu hỏi</Dialog.Title>
          <Dialog.Description className={styles.modalDescription}>
            Chia sẻ tình huống của bạn để nhận thêm góc nhìn từ cộng đồng.
          </Dialog.Description>
          <form id="community-question-form" className={styles.form} onSubmit={submit}>
            <label className={styles.field}>
              <span className={styles.fieldLabel}>Chủ đề</span>
              <select
                className={styles.fieldControl}
                name="topicSlug"
                required
                value={topicSlug || topics[0]?.slug || ''}
                onChange={(event) => setTopicSlug(event.target.value)}
              >
                {topics.length === 0 && <option value="">Chưa có chủ đề</option>}
                {topics.map((topic) => (
                  <option key={topic.id} value={topic.slug}>
                    {topic.name}
                  </option>
                ))}
              </select>
            </label>
            <label className={styles.field}>
              <span className={styles.fieldLabel}>Tên hiển thị <span className="muted">(không bắt buộc)</span></span>
              <input
                className={styles.fieldControl}
                name="authorName"
                autoComplete="name"
                maxLength={120}
                placeholder="Có thể để trống để đăng ẩn danh"
                value={authorName}
                onChange={(event) => setAuthorName(event.target.value)}
              />
            </label>
            <label className={styles.field}>
              <span className={styles.fieldLabel}>Tiêu đề</span>
              <input
                className={styles.fieldControl}
                name="title"
                required
                minLength={5}
                maxLength={200}
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder="Tóm tắt tình huống của bạn"
              />
            </label>
            <label className={styles.field}>
              <span className={styles.fieldLabel}>Nội dung câu hỏi</span>
              <textarea
                className={`${styles.fieldControl} ${styles.textArea}`}
                name="questionContent"
                required
                minLength={10}
                maxLength={10000}
                value={questionContent}
                onChange={(event) => setQuestionContent(event.target.value)}
                placeholder="Nêu bối cảnh, thời điểm và điều bạn muốn được giải đáp…"
              />
              <span className={styles.formHint}>Không chia sẻ mã số thuế, số giấy tờ hoặc thông tin cá nhân nhạy cảm.</span>
            </label>
            {error && <p className={styles.formError} role="alert">{error}</p>}
          </form>
          <div className={styles.formActions}>
            <button className="button button-quiet" type="button" onClick={() => onOpenChange(false)} disabled={sending}>
              Để sau
            </button>
            <button className="button button-primary" type="submit" form="community-question-form" disabled={sending || topics.length === 0}>
              {sending ? 'Đang gửi…' : 'Gửi câu hỏi'}
            </button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
