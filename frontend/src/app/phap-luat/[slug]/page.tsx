import { LegalDocumentDetail } from '@/components/features/legal/LegalDocumentDetail';
import { AppShell } from '@/components/features/navigation/AppShell';

export default function LegalDocumentPage() {
  return (
    <AppShell active="legal">
      <LegalDocumentDetail />
    </AppShell>
  );
}
