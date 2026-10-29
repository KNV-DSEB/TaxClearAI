'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import { ApiError } from '@/services/api.client';
import { assessmentsService } from '@/services/assessments.service';
import type { Assessment } from '@/types/api.types';

import { AssessmentWorkspace } from './AssessmentWorkspace';

export function AssessmentLoader({ id }: { id: string }) {
  const router = useRouter();
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    const controller = new AbortController();
    async function load(): Promise<void> {
      try {
        setAssessment(await assessmentsService.get(id, controller.signal));
      } catch (error) {
        if (controller.signal.aborted) return;
        if (error instanceof ApiError && error.status === 401)
          router.replace(`/dang-nhap?returnTo=${encodeURIComponent(`/ho-so/${id}`)}`);
        else setError(error instanceof Error ? error.message : 'Chưa mở được hồ sơ.');
      }
    }
    void load();
    return () => controller.abort();
  }, [id, router]);

  if (assessment) return <AssessmentWorkspace initial={assessment} />;
  return (
    <section className="surface loading-panel">
      {error ? (
        <>
          <p role="alert">{error}</p>
          <Link href="/khao-sat" className="button button-secondary">
            Mở khảo sát mới
          </Link>
        </>
      ) : (
        <p role="status">Đang mở hồ sơ đã lưu…</p>
      )}
    </section>
  );
}
