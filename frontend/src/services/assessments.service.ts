import type {
  Answers,
  Assessment,
  ChecklistItem,
  ItemStatus,
  Questionnaire,
} from '@/types/api.types';

import { apiData, apiFetch } from './api.client';

export const assessmentsService = {
  async questionnaire(signal?: AbortSignal): Promise<Questionnaire> {
    return apiData<Questionnaire>('/api/v1/questionnaires/b2', { signal });
  },
  async create(questionnaireVersion: string, answers: Answers): Promise<Assessment> {
    return apiData<Assessment>('/api/v1/assessments', {
      method: 'POST',
      body: JSON.stringify({ questionnaireVersion, answers }),
    });
  },
  async get(id: string, signal?: AbortSignal): Promise<Assessment> {
    return apiData<Assessment>(`/api/v1/assessments/${encodeURIComponent(id)}`, { signal });
  },
  async updateItem(id: string, itemId: string, status: ItemStatus): Promise<ChecklistItem> {
    return apiData<ChecklistItem>(
      `/api/v1/assessments/${encodeURIComponent(id)}/checklist-items/${encodeURIComponent(itemId)}`,
      {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      },
    );
  },
  async remove(id: string): Promise<void> {
    await apiFetch<void>(`/api/v1/assessments/${encodeURIComponent(id)}`, { method: 'DELETE' });
  },
};
