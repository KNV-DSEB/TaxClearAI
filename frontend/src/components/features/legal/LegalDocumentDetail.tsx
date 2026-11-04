'use client';

import {
  ArrowLeft,
  ArrowUpRight,
  Building2,
  Check,
  Clock3,
  FileCheck2,
  Landmark,
} from 'lucide-react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

import { legalService } from '@/services/legal.service';
import type { LegalDocument } from '@/types/legal.types';

import styles from './LegalLibrary.module.css';

export function LegalDocumentDetail() {
  const params = useParams<{ slug: string }>();
  const [document, setDocument] = useState<LegalDocument | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    legalService
      .getDocument(params.slug, controller.signal)
      .then(setDocument)
      .catch((requestError: unknown) => {
        if (!controller.signal.aborted) {
          setError(requestError instanceof Error ? requestError.message : 'Không tải được tài liệu.');
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setIsLoading(false);
      });
    return () => controller.abort();
  }, [params.slug]);

  if (isLoading) return <main id="main-content" className={`page ${styles.page}`}><p className={styles.status}>Đang tải hướng dẫn…</p></main>;
  if (error || !document) {
    return (
      <main id="main-content" className={`page ${styles.page}`}>
        <Link className={styles.backLink} href="/phap-luat"><ArrowLeft size={16} /> Trở về thư viện</Link>
        <p className={styles.error} role="alert">{error || 'Không tìm thấy tài liệu này.'}</p>
      </main>
    );
  }

  return (
    <main id="main-content" className={`page ${styles.page}`}>
      <Link className={styles.backLink} href="/phap-luat"><ArrowLeft size={16} /> Thư viện pháp luật</Link>
      <header className={styles.detailHero}>
        <div>
          <span className={styles.eyebrow}><Landmark size={15} /> {document.documentType}</span>
          <span className={styles.detailNumber}>{document.documentNumber}</span>
          <h1>{document.documentTitle}</h1>
          <p>{document.summary}</p>
          <span className={styles.authority}><Building2 size={15} /> {document.authority}</span>
        </div>
        <div className={styles.heroSeal} aria-hidden="true"><span>THỦ TỤC</span><strong>PL</strong></div>
      </header>

      <div className={styles.detailGrid}>
        <div className={styles.mainColumn}>
          <section className={styles.contentPanel} aria-labelledby="overview-title">
            <div className={styles.panelHeading}><span>01</span><h2 id="overview-title">Tổng quan & căn cứ</h2></div>
            <p className={styles.overview}>{document.overview}</p>
            <h3 className={styles.subheading}>Ai cần áp dụng</h3>
            <div className={styles.appliesTags}>{document.appliesTo.map((item) => <span key={item}>{item}</span>)}</div>
            <h3 className={styles.subheading}>Căn cứ pháp lý</h3>
            <ul className={styles.basisList}>{document.legalBasis.map((item) => <li key={item}>{item}</li>)}</ul>
          </section>

          <section className={styles.contentPanel} aria-labelledby="steps-title">
            <div className={styles.panelHeading}><span>02</span><h2 id="steps-title">Các bước thực hiện</h2></div>
            <ol className={styles.timeline}>
              {document.processSteps.map((step, index) => (
                <li key={step.title}>
                  <span className={styles.stepNumber}>{String(index + 1).padStart(2, '0')}</span>
                  <div>
                    <h3>{step.title}</h3>
                    <p>{step.description}</p>
                    {step.authority && <span className={styles.stepMeta}><Building2 size={14} /> {step.authority}</span>}
                    {step.timing && <span className={styles.stepMeta}><Clock3 size={14} /> {step.timing}</span>}
                  </div>
                </li>
              ))}
            </ol>
          </section>

          <section className={styles.contentPanel} aria-labelledby="checklist-title">
            <div className={styles.panelHeading}><span>03</span><h2 id="checklist-title">Checklist hồ sơ</h2></div>
            <ul className={styles.checklist}>
              {document.checklist.map((item) => <li key={item}><Check size={16} /> <span>{item}</span></li>)}
            </ul>
          </section>
        </div>

        <aside className={styles.sideColumn}>
          <section className={styles.timelineCard}>
            <span><Clock3 size={16} /> THỜI HẠN</span>
            <p>{document.timeline}</p>
          </section>
          {document.notes.length > 0 && (
            <section className={styles.noteCard}>
              <h2><FileCheck2 size={18} /> Lưu ý trước khi nộp</h2>
              <ul>{document.notes.map((note) => <li key={note}>{note}</li>)}</ul>
            </section>
          )}
          <section className={styles.sourcesCard}>
            <h2>Nguồn tham chiếu</h2>
            <p>Ưu tiên nguồn chính thức; đường dẫn tham khảo được gắn nhãn rõ ràng.</p>
            <ul>
              {document.sources.map((source) => (
                <li key={source.url}>
                  <a href={source.url} target="_blank" rel="noreferrer">
                    <span>{source.label}<small>{source.sourceType === 'official' ? 'Nguồn chính thức' : 'Nguồn tham khảo'}</small></span>
                    <ArrowUpRight size={16} />
                  </a>
                </li>
              ))}
            </ul>
          </section>
        </aside>
      </div>
      <div className={styles.bottomBack}><Link className="button button-secondary" href="/phap-luat"><ArrowLeft size={16} /> Về danh sách tài liệu</Link></div>
    </main>
  );
}
