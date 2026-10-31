import { AssessmentLoader } from '@/components/features/assessments/AssessmentLoader';
import { AppShell } from '@/components/features/navigation/AppShell';

export default async function AssessmentPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <AppShell active="cases">
      <main id="main-content" className="page">
        <AssessmentLoader key={id} id={id} />
      </main>
    </AppShell>
  );
}
