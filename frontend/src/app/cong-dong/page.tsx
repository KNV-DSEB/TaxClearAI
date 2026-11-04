import { CommunityWorkspace } from '@/components/features/community/CommunityWorkspace';
import { AppShell } from '@/components/features/navigation/AppShell';

export default async function CommunityPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string | string[]; topic?: string | string[]; page?: string | string[] }>;
}) {
  const params = await searchParams;
  const keyword = typeof params.q === 'string' ? params.q : '';
  const topic = typeof params.topic === 'string' ? params.topic : '';
  const pageValue = Number(typeof params.page === 'string' ? params.page : '1');
  const page = Number.isInteger(pageValue) && pageValue > 0 ? Math.min(pageValue, 1000) : 1;

  return (
    <AppShell active="community">
      <main id="main-content" className="page">
        <CommunityWorkspace initialFilters={{ keyword, topic, page }} />
      </main>
    </AppShell>
  );
}
