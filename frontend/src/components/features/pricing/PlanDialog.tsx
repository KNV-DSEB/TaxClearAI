'use client';

import * as Dialog from '@radix-ui/react-dialog';
import { MessageCircleQuestion, X } from 'lucide-react';
import Link from 'next/link';

import { PlanStatus, getPlan } from './PlanParts';
import styles from './Pricing.module.css';

export interface ChecklistCounts {
  available: number;
  missing: number;
  needsVerification: number;
}

export function PlanDialog({
  open,
  onOpenChange,
  counts,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  counts: ChecklistCounts;
}) {
  const free = getPlan('free');
  const support = getPlan('support');
  const expert = getPlan('expert');
  // Chỉ hiện nhóm có mục, tránh dãy "0 đã có, 0 còn thiếu" gây nhiễu
  const chips = [
    { count: counts.available, label: 'đã có' },
    { count: counts.missing, label: 'còn thiếu' },
    { count: counts.needsVerification, label: 'cần xác minh' },
  ].filter((chip) => chip.count > 0);

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className={styles.overlay} />
        <Dialog.Content className={styles.dialog}>
          <Dialog.Title className={styles.dialogTitle}>
            Đã có danh mục giấy tờ cho hồ sơ của bạn
          </Dialog.Title>
          <Dialog.Description className={styles.dialogLead}>
            Bạn muốn đi tiếp thế nào? Phần miễn phí vẫn dùng được đầy đủ.
          </Dialog.Description>
          {chips.length > 0 && (
            <ul className={styles.counts} aria-label="Tình trạng danh mục giấy tờ">
              {chips.map((chip) => (
                <li key={chip.label}>
                  {chip.count} {chip.label}
                </li>
              ))}
            </ul>
          )}

          <ol className={styles.routes}>
            <li className={styles.route}>
              <span className={styles.step} aria-hidden="true">
                1
              </span>
              <div className={`${styles.routeBody} ${styles.routeBodyMain}`}>
                <div className={styles.routeTop}>
                  <h3>Tiếp tục miễn phí</h3>
                  <PlanStatus plan={free} />
                </div>
                <p className={styles.routePrice}>{free.price}</p>
                <p className={styles.routeText}>
                  Xem hồ sơ, đánh dấu giấy tờ, đọc thư viện pháp luật và hỏi đáp AI có dẫn nguồn.
                </p>
                <div className={styles.routeActions}>
                  <Dialog.Close asChild>
                    <button className="button button-primary" type="button">
                      Xem hồ sơ của tôi
                    </button>
                  </Dialog.Close>
                  <Link className="button button-outline" href="/hoi-dap">
                    <MessageCircleQuestion aria-hidden="true" size={16} /> Hỏi AI tiếp
                  </Link>
                </div>
              </div>
            </li>

            <li className={styles.route}>
              <span className={styles.step} aria-hidden="true">
                2
              </span>
              <div className={styles.routeBody}>
                <div className={styles.routeTop}>
                  <h3>{support.name}</h3>
                  <PlanStatus plan={support} />
                </div>
                <p className={styles.routePrice}>
                  {support.price} <span>{support.priceNote}</span>
                </p>
                <p className={styles.routeText}>
                  Theo dõi hồ sơ 90 ngày và hỏi đáp AI không giới hạn lượt. Gói này chưa mở bán.
                </p>
                <div className={styles.routeActions}>
                  <Link className="button button-outline" href="/bang-gia#goi-ho-tro">
                    Xem gói này
                  </Link>
                </div>
              </div>
            </li>

            <li className={styles.route}>
              <span className={styles.step} aria-hidden="true">
                3
              </span>
              <div className={styles.routeBody}>
                <div className={styles.routeTop}>
                  <h3>{expert.name}</h3>
                  <PlanStatus plan={expert} />
                </div>
                <p className={styles.routePrice}>
                  {expert.price} <span>{expert.priceNote}</span>
                </p>
                <p className={styles.routeText}>
                  Với hồ sơ có tồn đọng phức tạp, chuyển bản tổng hợp cho chuyên gia. Hiện bạn gửi
                  được yêu cầu tới hồ sơ đối tác mẫu.
                </p>
                <div className={styles.routeActions}>
                  <Dialog.Close asChild>
                    <a className="button button-outline" href="#experts">
                      Xem chuyên gia phù hợp
                    </a>
                  </Dialog.Close>
                </div>
              </div>
            </li>
          </ol>

          <p className={styles.dialogFoot}>
            Bản thử chưa thu phí. Giá là dự kiến để kiểm chứng với người dùng.{' '}
            <Link href="/bang-gia">Xem bảng giá đầy đủ</Link>
          </p>

          <Dialog.Close asChild>
            <button aria-label="Đóng" className={styles.dialogClose} type="button">
              <X aria-hidden="true" size={18} />
            </button>
          </Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
