import { AssessmentList } from '@/components/features/assessments/AssessmentList';
import { AppShell } from '@/components/features/navigation/AppShell';

export default function CasesPage() {
  return (
    <AppShell active="cases">
      <main id="main-content" className="content-main">
        <AssessmentList />
      </main>
    </AppShell>
  );
}
