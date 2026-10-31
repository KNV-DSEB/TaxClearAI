import { PrintSummary } from '@/components/features/assessments/PrintSummary';
import { AppShell } from '@/components/features/navigation/AppShell';

export default async function PrintPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <AppShell active="cases">
      <main id="main-content" className="page">
        <PrintSummary key={id} id={id} />
      </main>
    </AppShell>
  );
}
