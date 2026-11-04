import Image from 'next/image';
import { BadgeCheck, Building2, MapPin, ShieldCheck } from 'lucide-react';

import type { Expert } from '@/types/experts.types';

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

export function ExpertCard({ expert, onBook }: { expert: Expert; onBook: (expert: Expert) => void }) {
  const partnerLabels = {
    accounting_firm: 'Công ty kế toán',
    accountant: 'Kế toán dịch vụ',
    tax_consultant: 'Chuyên gia tư vấn',
  };
  const partnerStyles = {
    accounting_firm: styles.partnerFirm,
    accountant: styles.partnerAccountant,
    tax_consultant: styles.partnerConsultant,
  };
  return (
    <li className={styles.expertCard}>
      <div className={styles.profileHeader}>
        <span className={styles.avatar}>
          {expert.avatarUrl ? (
            <Image
              className={styles.avatarImage}
              src={expert.avatarUrl}
              alt={`Ảnh đại diện ${expert.fullName}`}
              width={64}
              height={64}
              unoptimized
            />
          ) : (
            <span aria-hidden="true">{initials(expert.fullName)}</span>
          )}
        </span>
        <div className={styles.identity}>
          <span className={`${styles.partnerBadge} ${partnerStyles[expert.partnerType]}`}>
            {partnerLabels[expert.partnerType]}
          </span>
          <h2 className={styles.name}>{expert.fullName}</h2>
          <p className={styles.title}>{expert.title}</p>
          <span className={`${styles.verification} ${!expert.isVerified ? styles.verificationPending : ''}`}>
            {expert.isVerified ? <BadgeCheck size={13} aria-hidden /> : <ShieldCheck size={13} aria-hidden />}
            {expert.isVerified ? 'Đã xác thực chứng chỉ' : 'Thông tin chưa xác minh'}
          </span>
        </div>
      </div>

      <p className={styles.organization}><Building2 size={15} aria-hidden /> {expert.organization}</p>
      <div className={styles.facts}>
        <span className={styles.fact}><ShieldCheck size={14} aria-hidden /> {expert.experienceYears} năm kinh nghiệm</span>
        <span className={styles.fact}><MapPin size={14} aria-hidden /> {expert.location}</span>
      </div>

      <div className={styles.specializations} aria-label="Chuyên môn">
        {expert.specializations.map((item) => <span className={styles.tag} key={item}>{item}</span>)}
      </div>
      {expert.servicesOffered.length > 0 && (
        <div className={styles.services} aria-label="Dịch vụ cung cấp">
          <strong>Dịch vụ</strong>
          <p>{expert.servicesOffered.join(' · ')}</p>
        </div>
      )}
      <p className={styles.bio}>{expert.bio}</p>

      <div className={styles.cardFooter}>
        <div>
          <span className={styles.feeLabel}>Phí tư vấn tham khảo</span>
          <strong className={styles.fee}>{expert.consultationFeeText}</strong>
        </div>
        <button className={`button button-primary ${styles.bookButton}`} type="button" onClick={() => onBook(expert)}>
          Đặt lịch tư vấn
        </button>
      </div>
    </li>
  );
}
