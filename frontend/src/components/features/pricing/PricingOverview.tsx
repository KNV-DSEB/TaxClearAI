import { ArrowRight, Info } from 'lucide-react';
import Link from 'next/link';

import { PlanFeatures, PlanStatus } from './PlanParts';
import styles from './Pricing.module.css';
import { FAQ, PLANS, TRIAL_NOTICE, type Plan } from './pricing-plans';

const ANCHORS: Record<Plan['id'], string> = {
  free: 'goi-mien-phi',
  support: 'goi-ho-tro',
  expert: 'goi-chuyen-gia',
};

function PlanAction({ plan }: { plan: Plan }) {
  if (plan.id === 'free') {
    return (
      <Link className="button button-primary" href="/khao-sat">
        Dùng thử miễn phí <ArrowRight aria-hidden="true" size={16} />
      </Link>
    );
  }
  if (plan.id === 'expert') {
    return (
      <Link className="button button-outline" href="/chuyen-gia">
        Xem hồ sơ chuyên gia mẫu
      </Link>
    );
  }
  return <p className="small muted">Chưa mở bán. Hiện bạn dùng được miễn phí.</p>;
}

export function PricingOverview() {
  return (
    <div className={styles.page}>
      <header className={styles.intro}>
        <h1>Bảng giá</h1>
        <p>
          Bắt đầu miễn phí. Chỉ trả tiền khi bạn cần được theo dõi hồ sơ sát hơn hoặc cần chuyên gia
          xử lý phần phức tạp.
        </p>
      </header>

      <p className={styles.notice} role="note">
        <Info aria-hidden="true" size={18} />
        <span>{TRIAL_NOTICE}</span>
      </p>

      <ol className={styles.grid} aria-label="Ba mức hỗ trợ">
        {PLANS.map((plan) => (
          <li key={plan.id}>
            <article
              className={`${styles.card} ${plan.available ? styles.cardCurrent : ''}`}
              id={ANCHORS[plan.id]}
              aria-labelledby={`${ANCHORS[plan.id]}-title`}
            >
              <div className={styles.cardHead}>
                <span className={styles.step} aria-hidden="true">
                  {plan.step}
                </span>
                <PlanStatus plan={plan} />
              </div>
              <h2 id={`${ANCHORS[plan.id]}-title`}>{plan.name}</h2>
              <p>{plan.summary}</p>
              <p className={styles.price}>
                {plan.price}
                <span className={styles.priceNote}>{plan.priceNote}</span>
              </p>
              <PlanFeatures plan={plan} />
              <div className={styles.cardFoot}>
                <PlanAction plan={plan} />
              </div>
            </article>
          </li>
        ))}
      </ol>

      <section className={styles.faq} aria-labelledby="faq-title">
        <h2 id="faq-title">Câu hỏi thường gặp</h2>
        {FAQ.map((item) => (
          <details key={item.question}>
            <summary>{item.question}</summary>
            <p>{item.answer}</p>
          </details>
        ))}
      </section>

      <section className={styles.closing} aria-label="Bắt đầu">
        <p>Thử ngay với tình trạng của doanh nghiệp bạn. Không cần tải giấy tờ hay nhập số thuế.</p>
        <Link className="button button-primary" href="/khao-sat">
          Bắt đầu chuẩn bị hồ sơ <ArrowRight aria-hidden="true" size={16} />
        </Link>
      </section>
    </div>
  );
}
