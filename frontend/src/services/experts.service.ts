import type {
  ConsultationFormValues,
  ConsultationResponse,
  Expert,
  ExpertQuery,
  RecommendedExpert,
} from '@/types/experts.types';

import { apiData } from './api.client';

interface ExpertPage {
  items: Expert[];
  page: number;
  pageSize: number;
  total: number;
}

export const expertsService = {
  async getExperts(params: ExpertQuery = {}, signal?: AbortSignal): Promise<Expert[]> {
    const query = new URLSearchParams({ page: '1', pageSize: '100' });
    if (params.q?.trim()) query.set('q', params.q.trim());
    if (params.specialization) query.set('specialization', params.specialization);
    if (params.location) query.set('location', params.location);
    if (params.partnerType) query.set('partnerType', params.partnerType);
    const result = await apiData<ExpertPage>(`/api/v1/experts/?${query.toString()}`, { signal });
    return result.items;
  },

  async getExpertDetail(id: string, signal?: AbortSignal): Promise<Expert> {
    return apiData<Expert>(`/api/v1/experts/${encodeURIComponent(id)}`, { signal });
  },

  async getRecommendedExperts(
    assessmentId: string,
    signal?: AbortSignal,
  ): Promise<RecommendedExpert[]> {
    const result = await apiData<Array<{ expert: Expert; matchReason: string }>>(
      `/api/v1/experts/recommendations/${encodeURIComponent(assessmentId)}`,
      { signal },
    );
    return result.map(({ expert, matchReason }) => ({ expert, match_reason: matchReason }));
  },

  async submitConsultation(data: ConsultationFormValues): Promise<ConsultationResponse> {
    return apiData<ConsultationResponse>('/api/v1/experts/consultations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};
