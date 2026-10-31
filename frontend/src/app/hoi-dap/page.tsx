import { ChatWorkspace } from '@/components/features/chat/ChatWorkspace';
import { AppShell } from '@/components/features/navigation/AppShell';

export default function ChatPage() {
  return (
    <AppShell active="chat">
      <main id="main-content" className="page">
        <ChatWorkspace />
      </main>
    </AppShell>
  );
}
