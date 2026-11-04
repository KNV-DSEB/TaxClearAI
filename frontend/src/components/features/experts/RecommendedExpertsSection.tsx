'use client';

import Image from 'next/image';
import { BadgeCheck, Lightbulb, ShieldCheck } from 'lucide-react';
import { useEffect, useState } from 'react';

import { expertsService } from '@/services/experts.service';
import type { Expert, RecommendedExpert } from '@/types/experts.types';

import { ConsultationModal } from './ConsultationModal';
import styles from './Experts.module.css';

function initials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(-2)
    .map((part) => part[0])
    .join('')
    .toLocaleUpperCase('vi-VN');
}

export function RecommendedExpertsSection({
  assessmentId,
  initialNotes,
}: {
  assessmentId: string;
  initialNotes?: string;
}) {
  const [recommendations, setRecommendations] = useState<RecommendedExpert[]>([]);
  const [selectedExpert, setSelectedExpert] = useState<Expert | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    expertsService
      .getRecommendedExperts(assessmentId, controller.signal)
      .then(setRecommendations)
      .catch((requestError: unknown) => {
        if (!controller.signal.aborted) {
          setError(
            requestError instanceof Error
              ? requestError.message
              : 'Chưa tải được gợi ý chuyên gia. Vui lòng thử tải lại trang.',
          );
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [assessmentId]);

  return (
    <section className={styles.recommendationPanel} aria-labelledby="recommendation-heading">
      <header className={styles.recommendationHeader}>
        <span className={styles.recommendationSeal} aria-hidden="true">
          <ShieldCheck size={22} />
        </span>
        <div>
          <p className={styles.recommendationEyebrow}>Đề xuất theo hồ sơ</p>
          <h2 id="recommendation-heading" className={styles.recommendationTitle}>
            Chuyên gia phù hợp với hồ sơ của bạn
          </h2>
        </div>
      </header>

      {loading ? (
        <p className={styles.recommendationState} role="status">Đang tìm chuyên gia phù hợp…</p>
      ) : error ? (
        <p className={`${styles.recommendationState} ${styles.recommendationError}`} role="alert">
          {error}
        </p>
      ) : recommendations.length === 0 ? (
        <p className={styles.recommendationState}>
          Chưa tìm thấy chuyên gia phù hợp với thông tin hiện tại trong hồ sơ.
        </p>
      ) : (
        <ul className={styles.recommendationList}>
          {recommendations.slice(0, 2).map(({ expert, match_reason: matchReason }) => (
            <li className={styles.recommendationItem} key={expert.id}>
              <div className={styles.recommendationProfile}>
                <span className={styles.recommendationAvatar}>
                  {expert.avatarUrl ? (
                    <Image
                      src={expert.avatarUrl}
                      alt={`Ảnh đại diện ${expert.fullName}`}
                      width={54}
                      height={54}
                      unoptimized
                    />
                  ) : (
                    <span aria-hidden="true">{initials(expert.fullName)}</span>
                  )}
                </span>
                <div className={styles.recommendationIdentity}>
                  <h3>{expert.fullName}</h3>
                  <p>{expert.title}</p>
                  <span
                    className={`${styles.recommendationBadge} ${
                      !expert.isVerified ? styles.recommendationBadgePending : ''
                    }`}
                  >
                    <BadgeCheck size={13} aria-hidden />
                    {expert.isVerified ? 'Đã xác thực' : 'Chưa xác minh'}
                  </span>
                </div>
                <div className={styles.recommendationFee}>
                  <span>Phí tư vấn tham khảo</span>
                  <strong>{expert.consultationFeeText}</strong>
                </div>
              </div>

              <p className={styles.matchReason}>
                <Lightbulb size={16} aria-hidden />
                <span><strong>Lý do đề xuất:</strong> {matchReason}</span>
              </p>
              <button
                className={`button button-primary ${styles.connectButton}`}
                type="button"
                onClick={() => setSelectedExpert(expert)}
              >
                Kết nối với hồ sơ này
              </button>
            </li>
          ))}
        </ul>
      )}

      {selectedExpert && (
        <ConsultationModal
          key={`${selectedExpert.id}-${assessmentId}`}
          expert={selectedExpert}
          assessmentId={assessmentId}
          initialNotes={initialNotes}
          open
          onOpenChange={(open) => {
            if (!open) setSelectedExpert(null);
          }}
        />
      )}
    </section>
  );
}
