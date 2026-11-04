import { ExpertsWorkspace } from '@/components/features/experts/ExpertsWorkspace';
import { AppShell } from '@/components/features/navigation/AppShell';
import type { ExpertQuery } from '@/types/experts.types';

export default async function ExpertsPage({
  searchParams,
}: {
  searchParams: Promise<{
    q?: string | string[];
    specialization?: string | string[];
    location?: string | string[];
    assessmentId?: string | string[];
    partnerType?: string | string[];
  }>;
}) {
  const params = await searchParams;
  const initialFilters: ExpertQuery = {
    q: typeof params.q === 'string' ? params.q : '',
    specialization: typeof params.specialization === 'string' ? params.specialization : '',
    location: typeof params.location === 'string' ? params.location : '',
    partnerType:
      params.partnerType === 'accounting_firm' ||
      params.partnerType === 'accountant' ||
      params.partnerType === 'tax_consultant'
        ? params.partnerType
        : '',
  };

  return (
    <AppShell active="experts">
      <main id="main-content" className="page">
        <ExpertsWorkspace
          initialFilters={initialFilters}
          assessmentId={typeof params.assessmentId === 'string' ? params.assessmentId : undefined}
        />
      </main>
    </AppShell>
  );
}
