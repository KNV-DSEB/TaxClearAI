'use client';

import { BadgeHelp, SearchCheck } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';

import { expertsService } from '@/services/experts.service';
import type { Expert, ExpertQuery } from '@/types/experts.types';

import { ConsultationModal } from './ConsultationModal';
import { ExpertCard } from './ExpertCard';
import { ExpertFilterBar } from './ExpertFilterBar';
import styles from './Experts.module.css';

export function ExpertsWorkspace({
  initialFilters,
  assessmentId,
}: {
  initialFilters: ExpertQuery;
  assessmentId?: string;
}) {
  const [experts, setExperts] = useState<Expert[]>([]);
  const [keyword, setKeyword] = useState(initialFilters.q ?? '');
  const [specialization, setSpecialization] = useState(initialFilters.specialization ?? '');
  const [location, setLocation] = useState(initialFilters.location ?? '');
  const [partnerType, setPartnerType] = useState(initialFilters.partnerType ?? '');
  const [draftKeyword, setDraftKeyword] = useState(initialFilters.q ?? '');
  const [draftSpecialization, setDraftSpecialization] = useState(initialFilters.specialization ?? '');
  const [draftLocation, setDraftLocation] = useState(initialFilters.location ?? '');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);
  const [selectedExpert, setSelectedExpert] = useState<Expert | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      setLoading(true);
      try {
        setExperts(await expertsService.getExperts(
          { q: keyword, specialization, location, partnerType: partnerType || undefined },
          controller.signal,
        ));
        setError('');
      } catch (loadError) {
        if (!controller.signal.aborted) {
          setError(loadError instanceof Error ? loadError.message : 'Chưa tải được danh sách chuyên gia.');
        }
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }
    void load();
    return () => controller.abort();
  }, [keyword, specialization, location, partnerType, refreshKey]);

  useEffect(() => {
    function syncFromHistory() {
      const params = new URLSearchParams(window.location.search);
      const nextKeyword = params.get('q') ?? '';
      const nextSpecialization = params.get('specialization') ?? '';
      const nextLocation = params.get('location') ?? '';
      const nextPartnerType = params.get('partnerType') ?? '';
      setKeyword(nextKeyword);
      setDraftKeyword(nextKeyword);
      setSpecialization(nextSpecialization);
      setDraftSpecialization(nextSpecialization);
      setLocation(nextLocation);
      setDraftLocation(nextLocation);
      setPartnerType(
        nextPartnerType === 'accounting_firm' || nextPartnerType === 'accountant' || nextPartnerType === 'tax_consultant'
          ? nextPartnerType
          : '',
      );
    }
    window.addEventListener('popstate', syncFromHistory);
    return () => window.removeEventListener('popstate', syncFromHistory);
  }, []);

  const updateUrl = useCallback((filters: ExpertQuery) => {
    const params = new URLSearchParams();
    if (filters.q?.trim()) params.set('q', filters.q.trim());
    if (filters.specialization) params.set('specialization', filters.specialization);
    if (filters.location) params.set('location', filters.location);
    if (partnerType) params.set('partnerType', partnerType);
    if (assessmentId) params.set('assessmentId', assessmentId);
    const query = params.toString();
    window.history.pushState({}, '', query ? `/chuyen-gia?${query}` : '/chuyen-gia');
  }, [assessmentId, partnerType]);

  function search() {
    const filters = {
      q: draftKeyword.trim(),
      specialization: draftSpecialization,
      location: draftLocation,
    };
    setKeyword(filters.q);
    setSpecialization(filters.specialization);
    setLocation(filters.location);
    updateUrl(filters);
  }

  return (
    <div className={styles.workspace}>
      <section className={styles.hero} aria-labelledby="experts-title">
        <div className={styles.heroCopy}>
          <span className={styles.eyebrow}><BadgeHelp size={15} aria-hidden /> Chuyên gia hỗ trợ</span>
          <h1 id="experts-title" className={styles.heroTitle}>Đúng người đồng hành.<br />Rõ bước xử lý tiếp theo.</h1>
          <p className={styles.heroText}>
            Tìm chuyên gia theo lĩnh vực và khu vực, rồi gửi yêu cầu tư vấn phù hợp với tình huống của bạn.
          </p>
        </div>
      </section>

      <ExpertFilterBar
        keyword={draftKeyword}
        specialization={draftSpecialization}
        location={draftLocation}
        onKeywordChange={setDraftKeyword}
        onSpecializationChange={setDraftSpecialization}
        onLocationChange={setDraftLocation}
        onSearch={search}
      />

      <nav className={styles.partnerTabs} aria-label="Lọc theo nhóm đối tác">
        {([
          ['', 'Tất cả'],
          ['accounting_firm', 'Công ty kế toán'],
          ['accountant', 'Người làm kế toán'],
          ['tax_consultant', 'Chuyên gia tư vấn'],
        ] as const).map(([type, label]) => (
          <button
            key={type || 'all'}
            className={`${styles.partnerTab} ${partnerType === type ? styles.partnerTabActive : ''}`}
            type="button"
            aria-pressed={partnerType === type}
            onClick={() => {
              setPartnerType(type);
              const params = new URLSearchParams(window.location.search);
              if (type) params.set('partnerType', type);
              else params.delete('partnerType');
              if (assessmentId) params.set('assessmentId', assessmentId);
              window.history.pushState({}, '', `/chuyen-gia${params.size ? `?${params}` : ''}`);
            }}
          >
            {label}
          </button>
        ))}
      </nav>

      <section aria-labelledby="expert-list-title">
        <div className={styles.resultHeading}>
          <div>
            <h2 id="expert-list-title" className={styles.resultTitle}>Danh sách chuyên gia</h2>
            <p className={styles.resultCount}>{loading ? 'Đang cập nhật hồ sơ…' : `${experts.length} hồ sơ phù hợp`}</p>
          </div>
          <SearchCheck size={22} color="var(--teal)" aria-hidden />
        </div>

        {error && (
          <div className={`${styles.statePanel} ${styles.stateError}`} role="alert">
            <p>{error}</p>
            <button className="text-link" type="button" onClick={() => setRefreshKey((value) => value + 1)}>
              Thử tải lại
            </button>
          </div>
        )}
        {loading && experts.length === 0 && !error && (
          <p className={styles.statePanel} role="status">Đang tải hồ sơ chuyên gia…</p>
        )}
        {!loading && !error && experts.length === 0 && (
          <div className={styles.statePanel}>
            <h3 className={styles.stateTitle}>Chưa tìm thấy chuyên gia phù hợp</h3>
            <p>Thử bỏ bớt bộ lọc hoặc tìm bằng một từ khóa khác.</p>
          </div>
        )}
        {experts.length > 0 && (
          <ul className={styles.expertGrid} aria-label="Hồ sơ chuyên gia">
            {experts.map((expert) => (
              <ExpertCard key={expert.id} expert={expert} onBook={setSelectedExpert} />
            ))}
          </ul>
        )}
      </section>

      {selectedExpert && (
        <ConsultationModal
          key={selectedExpert.id}
          expert={selectedExpert}
          assessmentId={assessmentId}
          open
          onOpenChange={(open) => {
            if (!open) setSelectedExpert(null);
          }}
        />
      )}
    </div>
  );
}
