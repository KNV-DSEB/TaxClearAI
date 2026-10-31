import { QuestionnaireForm } from '@/components/features/assessments/QuestionnaireForm';
import { AppShell } from '@/components/features/navigation/AppShell';

export default function SurveyPage() {
  return (
    <AppShell active="survey">
      <main id="main-content" className="page">
        <QuestionnaireForm />
      </main>
    </AppShell>
  );
}
