import { Check } from 'lucide-react';

import { PLANS, type Plan, type PlanId } from './pricing-plans';
import styles from './Pricing.module.css';

export function getPlan(id: PlanId): Plan {
  const plan = PLANS.find((item) => item.id === id);
  if (!plan) throw new Error(`Không có gói ${id}`);
  return plan;
}

export function PlanStatus({ plan }: { plan: Plan }) {
  return (
    <span
      className={`${styles.status} ${plan.available ? styles.statusOpen : styles.statusPlanned}`}
    >
      {plan.statusLabel}
    </span>
  );
}

export function PlanFeatures({ plan }: { plan: Plan }) {
  return (
    <ul className={styles.features} aria-label={`Tính năng của gói ${plan.name}`}>
      {plan.features.map((feature) => (
        <li key={feature.text}>
          <Check aria-hidden="true" size={16} />
          <span>
            {feature.text}
            {feature.planned && <span className={styles.planned}>Dự kiến</span>}
          </span>
        </li>
      ))}
    </ul>
  );
}
