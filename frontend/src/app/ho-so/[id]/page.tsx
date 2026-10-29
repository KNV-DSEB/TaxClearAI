import { AssessmentLoader } from '@/components/features/assessments/AssessmentLoader';
import { AppShell } from '@/components/features/navigation/AppShell';

export default async function AssessmentPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <AppShell active="survey">
      <main id="main-content" className="content-main">
        <AssessmentLoader key={id} id={id} />
      </main>
    </AppShell>
  );
}
