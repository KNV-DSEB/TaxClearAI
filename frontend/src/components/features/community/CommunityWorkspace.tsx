'use client';

import { BookOpenCheck, ChevronLeft, ChevronRight, UsersRound } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';

import { communityService } from '@/services/community.service';
import type { CommunityQuestionPage, CommunityTopic } from '@/types/community.types';

import { AskQuestionModal } from './AskQuestionModal';
import { CommunityFilterBar } from './CommunityFilterBar';
import { CommunityQuestionList } from './CommunityQuestionList';
import styles from './Community.module.css';

const PAGE_SIZE = 10;

export interface CommunityInitialFilters {
  keyword: string;
  topic: string;
  page: number;
}

export function CommunityWorkspace({ initialFilters }: { initialFilters: CommunityInitialFilters }) {
  const [topics, setTopics] = useState<CommunityTopic[]>([]);
  const [pageData, setPageData] = useState<CommunityQuestionPage | null>(null);
  const [keyword, setKeyword] = useState(initialFilters.keyword);
  const [topicSlug, setTopicSlug] = useState(initialFilters.topic);
  const [draftKeyword, setDraftKeyword] = useState(initialFilters.keyword);
  const [draftTopicSlug, setDraftTopicSlug] = useState(initialFilters.topic);
  const [page, setPage] = useState(initialFilters.page);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [askOpen, setAskOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    async function loadTopics() {
      try {
        setTopics(await communityService.getTopics(controller.signal));
      } catch (loadError) {
        if (!controller.signal.aborted) {
          setError(loadError instanceof Error ? loadError.message : 'Chưa tải được danh sách chủ đề.');
        }
      }
    }
    void loadTopics();
    return () => controller.abort();
  }, []);

  useEffect(() => {
    function syncFromHistory() {
      const params = new URLSearchParams(window.location.search);
      const pageValue = Number(params.get('page') ?? '1');
      const nextKeyword = params.get('q') ?? '';
      const nextTopic = params.get('topic') ?? '';
      setKeyword(nextKeyword);
      setDraftKeyword(nextKeyword);
      setTopicSlug(nextTopic);
      setDraftTopicSlug(nextTopic);
      setPage(Number.isInteger(pageValue) && pageValue > 0 ? Math.min(pageValue, 1000) : 1);
    }
    window.addEventListener('popstate', syncFromHistory);
    return () => window.removeEventListener('popstate', syncFromHistory);
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    async function loadQuestions() {
      setLoading(true);
      try {
        setPageData(
          await communityService.getQuestions(
            { q: keyword, topic: topicSlug, page, pageSize: PAGE_SIZE },
            controller.signal,
          ),
        );
        setError('');
      } catch (loadError) {
        if (!controller.signal.aborted) {
          setError(loadError instanceof Error ? loadError.message : 'Chưa tải được danh sách câu hỏi.');
        }
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }
    void loadQuestions();
    return () => controller.abort();
  }, [keyword, topicSlug, page, refreshKey]);

  const updateUrl = useCallback((nextKeyword: string, nextTopic: string, nextPage: number) => {
    const params = new URLSearchParams();
    if (nextKeyword.trim()) params.set('q', nextKeyword.trim());
    if (nextTopic) params.set('topic', nextTopic);
    if (nextPage > 1) params.set('page', String(nextPage));
    const query = params.toString();
    window.history.pushState({}, '', query ? `/cong-dong?${query}` : '/cong-dong');
  }, []);

  function search() {
    setKeyword(draftKeyword.trim());
    setTopicSlug(draftTopicSlug);
    setPage(1);
    updateUrl(draftKeyword, draftTopicSlug, 1);
  }

  function changePage(nextPage: number) {
    setPage(nextPage);
    updateUrl(keyword, topicSlug, nextPage);
  }

  const total = pageData?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className={styles.workspace}>
      <section className={styles.hero} aria-labelledby="community-title">
        <div className={styles.heroCopy}>
          <span className={styles.heroLabel}><BookOpenCheck size={15} aria-hidden /> Hồ sơ tình huống</span>
          <h1 id="community-title" className={styles.heroTitle}>Tình huống thật.<br />Góc nhìn rõ ràng.</h1>
          <p className={styles.heroText}>
            Tìm câu trả lời từ những câu chuyện doanh nghiệp đã gặp, hoặc chia sẻ tình huống của bạn với cộng đồng.
          </p>
        </div>
        <div className={styles.heroMetric} aria-label={`${topics.length} chủ đề đang hoạt động`}>
          <span className={styles.metricNumber}>{topics.length.toString().padStart(2, '0')}</span>
          <span className={styles.metricCaption}><UsersRound size={14} aria-hidden /> Chủ đề đang hoạt động</span>
        </div>
      </section>

      <CommunityFilterBar
        topics={topics}
        keyword={draftKeyword}
        topic={draftTopicSlug}
        onKeywordChange={setDraftKeyword}
        onTopicChange={setDraftTopicSlug}
        onSearch={search}
        onAsk={() => setAskOpen(true)}
      />

      <section aria-labelledby="question-list-title">
        <div className={styles.listHeading}>
          <div>
            <h2 id="question-list-title" className={styles.listTitle}>Hỏi đáp cộng đồng</h2>
            <p className={styles.listMeta}>
              {pageData ? `${total} tình huống` : 'Các câu hỏi và phản hồi đã được chia sẻ'}
              {topicSlug ? ` · ${topics.find((item) => item.slug === topicSlug)?.name ?? 'Chủ đề đã chọn'}` : ''}
            </p>
          </div>
          {loading && pageData && <span className="small muted" role="status">Đang cập nhật…</span>}
        </div>

        {error && (
          <div className={styles.errorState} role="alert">
            <p>{error}</p>
            <button className="text-link" type="button" onClick={() => setRefreshKey((value) => value + 1)}>
              Thử tải lại
            </button>
          </div>
        )}
        {loading && !pageData && !error && <p className={styles.loadingState} role="status">Đang tải tình huống…</p>}
        {pageData && <CommunityQuestionList items={pageData.items} />}
      </section>

      {pageData && totalPages > 1 && (
        <nav className={styles.pagination} aria-label="Phân trang câu hỏi">
          <button
            className={`button button-quiet ${styles.paginationButton}`}
            type="button"
            disabled={page <= 1 || loading}
            onClick={() => changePage(page - 1)}
          >
            <ChevronLeft size={16} aria-hidden /> Trước
          </button>
          <span aria-live="polite">Trang {page} / {totalPages}</span>
          <button
            className={`button button-quiet ${styles.paginationButton}`}
            type="button"
            disabled={page >= totalPages || loading}
            onClick={() => changePage(page + 1)}
          >
            Sau <ChevronRight size={16} aria-hidden />
          </button>
        </nav>
      )}

      <AskQuestionModal
        open={askOpen}
        topics={topics}
        onOpenChange={setAskOpen}
        onCreated={() => {
          setPage(1);
          setRefreshKey((value) => value + 1);
          updateUrl(keyword, topicSlug, 1);
        }}
      />
    </div>
  );
}
