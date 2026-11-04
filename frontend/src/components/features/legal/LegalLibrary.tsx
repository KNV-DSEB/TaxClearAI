'use client';

import {
  ArrowUpRight,
  BookOpenText,
  Building2,
  FileText,
  Search,
} from 'lucide-react';
import Link from 'next/link';
import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

import { legalService } from '@/services/legal.service';
import type { LegalCategory, LegalDocument } from '@/types/legal.types';

import styles from './LegalLibrary.module.css';

const FILTERS: { label: string; value: LegalCategory | '' }[] = [
  { label: 'Tất cả', value: '' },
  { label: 'Hộ kinh doanh', value: 'household' },
  { label: 'Giải thể doanh nghiệp', value: 'company_dissolution' },
  { label: 'Đóng mã số thuế', value: 'tax_closure' },
  { label: 'Công văn hướng dẫn', value: 'guidance' },
];

function isLegalCategory(value: string | null): value is LegalCategory {
  return FILTERS.some((filter) => filter.value === value && value !== '');
}

function LibraryContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const query = searchParams.get('q') ?? '';
  const categoryValue = searchParams.get('category');
  const category = isLegalCategory(categoryValue) ? categoryValue : '';
  const [documents, setDocuments] = useState<LegalDocument[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    legalService
      .getDocuments(query, category, controller.signal)
      .then((result) => {
        setDocuments(result.items);
        setTotal(result.total);
        setError('');
        setIsLoading(false);
      })
      .catch(() => {
        if (!controller.signal.aborted) {
          setError('Chưa tải được thư viện. Hãy thử tải lại.');
          setIsLoading(false);
        }
      });
    return () => controller.abort();
  }, [query, category]);

  function updateFilters(nextQuery: string, nextCategory: LegalCategory | '') {
    const params = new URLSearchParams(searchParams.toString());
    if (nextQuery.trim()) params.set('q', nextQuery.trim());
    else params.delete('q');
    if (nextCategory) params.set('category', nextCategory);
    else params.delete('category');
    const suffix = params.size ? `?${params.toString()}` : '';
    router.replace(`/phap-luat${suffix}`, { scroll: false });
  }

  return (
    <main id="main-content" className={`page ${styles.page}`}>
      <section className={styles.hero} aria-labelledby="legal-title">
        <div className={styles.heroCopy}>
          <span className={styles.eyebrow}><BookOpenText size={15} /> THƯ VIỆN THỦ TỤC</span>
          <h1 id="legal-title">Tra cứu đúng bước, chuẩn bị đúng hồ sơ.</h1>
          <p>
            Hướng dẫn về giải thể, chấm dứt mã số thuế và hộ kinh doanh. Mỗi mục đều có
            checklist và đường dẫn để bạn đối chiếu nguồn.
          </p>
          <div className={styles.heroFoot}>
            <span><FileText size={15} /> {total || 5} tài liệu trọng tâm</span>
            <span><Building2 size={15} /> Cập nhật theo nguồn cơ quan nhà nước</span>
          </div>
        </div>
        <div className={styles.heroMark} aria-hidden="true">
          <span>HỒ SƠ</span><strong>PL</strong><i>01 — 05</i>
        </div>
      </section>

      <section className={styles.searchPanel} aria-label="Tìm kiếm tài liệu pháp luật">
        <form
          className={styles.searchForm}
          onSubmit={(event) => {
            event.preventDefault();
            const formData = new FormData(event.currentTarget);
            updateFilters(String(formData.get('q') ?? ''), category);
          }}
        >
          <label className={styles.searchField}>
            <Search size={19} aria-hidden="true" />
            <span className="sr-only">Tìm theo thủ tục, số hiệu hoặc nội dung</span>
            <input
              key={query}
              name="q"
              type="search"
              defaultValue={query}
              placeholder="Tìm theo thủ tục, số hiệu hoặc nội dung"
            />
          </label>
          <button className="button button-primary" type="submit">Tìm tài liệu</button>
        </form>
        <div className={styles.filterTabs} aria-label="Lọc theo danh mục">
          {FILTERS.map((filter) => (
            <button
              aria-pressed={category === filter.value}
              className={category === filter.value ? styles.filterActive : ''}
              key={filter.value || 'all'}
              onClick={() => updateFilters(query, filter.value)}
              type="button"
            >
              {filter.label}
            </button>
          ))}
        </div>
      </section>

      <section className={styles.results} aria-labelledby="results-title">
        <div className={styles.resultsHeading}>
          <div>
            <span className={styles.sectionKicker}>MỤC LỤC</span>
            <h2 id="results-title">Văn bản và thủ tục</h2>
          </div>
          {!isLoading && <span className={styles.resultCount}>{documents.length} kết quả</span>}
        </div>
        {isLoading ? (
          <p className={styles.status} role="status">Đang tải tài liệu…</p>
        ) : error ? (
          <p className={styles.error} role="alert">{error}</p>
        ) : documents.length === 0 ? (
          <div className={styles.emptyState}>
            <Search size={24} />
            <h3>Chưa có tài liệu phù hợp</h3>
            <p>Thử số hiệu văn bản khác hoặc xóa bộ lọc.</p>
            <button className="button button-secondary" onClick={() => updateFilters('', '')} type="button">
              Xóa bộ lọc
            </button>
          </div>
        ) : (
          <div className={styles.documentList}>
            {documents.map((document, index) => (
              <article className={styles.documentCard} key={document.slug}>
                <Link className={styles.documentMainLink} href={`/phap-luat/${document.slug}`}>
                  <div className={styles.cardIndex} aria-hidden="true">
                    <span>{String(index + 1).padStart(2, '0')}</span>
                    <i />
                  </div>
                  <div className={styles.cardBody}>
                    <div className={styles.cardMeta}>
                      <span className={styles.documentType}>{document.documentType}</span>
                      <span className={styles.documentNumber}>{document.documentNumber}</span>
                    </div>
                    <h3>{document.documentTitle}</h3>
                    <p className={styles.cardSummary}>{document.summary}</p>
                    <div className={styles.cardFooter}>
                      <span className={styles.authority}><Building2 size={14} /> {document.authority}</span>
                    </div>
                  </div>
                </Link>
                {document.sources[0] && (
                  <a
                    aria-label={`Mở nguồn: ${document.sources[0].label}`}
                    className={styles.sourceLink}
                    href={document.sources[0].url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Mở nguồn <ArrowUpRight size={15} />
                  </a>
                )}
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

export function LegalLibrary() {
  return (
    <Suspense fallback={<main className={`page ${styles.page}`}><p className={styles.status}>Đang mở thư viện…</p></main>}>
      <LibraryContent />
    </Suspense>
  );
}
