'use client';

import { Search } from 'lucide-react';
import type { FormEvent } from 'react';

import styles from './Experts.module.css';

const SPECIALIZATIONS = [
  'Giải thể DN',
  'Tái cấu trúc',
  'Quyết toán thuế',
  'Hộ kinh doanh',
  'Hóa đơn VAT',
  'Sổ sách kế toán',
  'Chuyển đổi mô hình',
  'Tạm ngừng kinh doanh',
  'Lập hộ mới',
];

const LOCATIONS = [
  { value: '', label: 'Tất cả khu vực' },
  { value: 'Hà Nội', label: 'Hà Nội' },
  { value: 'TP. Hồ Chí Minh', label: 'TP.HCM' },
  { value: 'Toàn quốc', label: 'Toàn quốc' },
];

export function ExpertFilterBar({
  keyword,
  specialization,
  location,
  onKeywordChange,
  onSpecializationChange,
  onLocationChange,
  onSearch,
}: {
  keyword: string;
  specialization: string;
  location: string;
  onKeywordChange: (value: string) => void;
  onSpecializationChange: (value: string) => void;
  onLocationChange: (value: string) => void;
  onSearch: () => void;
}) {
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSearch();
  }

  return (
    <form className={styles.filterPanel} onSubmit={submit} role="search">
      <label className={styles.field}>
        <span className={styles.fieldLabel}>Tìm chuyên gia</span>
        <input
          className={styles.fieldControl}
          type="search"
          name="q"
          autoComplete="off"
          placeholder="Tên hoặc đơn vị công tác"
          value={keyword}
          onChange={(event) => onKeywordChange(event.target.value)}
        />
      </label>
      <label className={styles.field}>
        <span className={styles.fieldLabel}>Chuyên môn</span>
        <select
          className={styles.fieldControl}
          name="specialization"
          value={specialization}
          onChange={(event) => onSpecializationChange(event.target.value)}
        >
          <option value="">Tất cả chuyên môn</option>
          {SPECIALIZATIONS.map((item) => (
            <option key={item} value={item}>{item}</option>
          ))}
        </select>
      </label>
      <label className={styles.field}>
        <span className={styles.fieldLabel}>Khu vực</span>
        <select
          className={styles.fieldControl}
          name="location"
          value={location}
          onChange={(event) => onLocationChange(event.target.value)}
        >
          {LOCATIONS.map((item) => (
            <option key={item.value || 'all'} value={item.value}>{item.label}</option>
          ))}
        </select>
      </label>
      <button className={`button button-primary ${styles.searchButton}`} type="submit">
        <Search size={16} aria-hidden /> Tìm kiếm
      </button>
    </form>
  );
}
