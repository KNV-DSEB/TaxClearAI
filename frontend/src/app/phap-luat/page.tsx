import { LegalLibrary } from '@/components/features/legal/LegalLibrary';
import { AppShell } from '@/components/features/navigation/AppShell';

export default function LegalLibraryPage() {
  return (
    <AppShell active="legal">
      <LegalLibrary />
    </AppShell>
  );
}
