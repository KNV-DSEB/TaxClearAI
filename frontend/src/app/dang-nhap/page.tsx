import { LoginForm } from '@/components/features/auth/LoginForm';
import { AppShell } from '@/components/features/navigation/AppShell';

export default function LoginPage() {
  return (
    <AppShell>
      <main id="main-content" className="content-main">
        <LoginForm />
      </main>
    </AppShell>
  );
}
