import { AssessmentList } from '@/components/features/assessments/AssessmentList';
import { AppShell } from '@/components/features/navigation/AppShell';
import type { CaseFilter } from '@/types/api.types';

const FILTERS: CaseFilter[] = ['all', 'in_progress', 'ready'];

export default async function CasesPage({
  searchParams,
}: {
  searchParams: Promise<{ 'trang-thai'?: string }>;
}) {
  const requested = (await searchParams)['trang-thai'];
  const filter = FILTERS.find((value) => value === requested) ?? 'all';
  return (
    <AppShell active="cases">
      <main id="main-content" className="page">
        <AssessmentList key={filter} filter={filter} />
      </main>
    </AppShell>
  );
}
