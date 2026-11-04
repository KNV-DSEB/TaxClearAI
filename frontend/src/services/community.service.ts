import { apiData } from './api.client';
import type {
  CommunityQuestion,
  CommunityQuestionPage,
  CommunityQuestionQuery,
  CommunityTopic,
  CreateCommunityQuestion,
} from '@/types/community.types';

export const communityService = {
  async getTopics(signal?: AbortSignal): Promise<CommunityTopic[]> {
    return apiData<CommunityTopic[]>('/api/v1/community/topics', { signal });
  },

  async getQuestions(
    { q, topic, page = 1, pageSize = 20 }: CommunityQuestionQuery,
    signal?: AbortSignal,
  ): Promise<CommunityQuestionPage> {
    const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) });
    if (q?.trim()) params.set('q', q.trim());
    if (topic) params.set('topic', topic);
    return apiData<CommunityQuestionPage>(`/api/v1/community/questions?${params.toString()}`, {
      signal,
    });
  },

  async getQuestion(id: string, signal?: AbortSignal): Promise<CommunityQuestion> {
    return apiData<CommunityQuestion>(
      `/api/v1/community/questions/${encodeURIComponent(id)}`,
      { signal },
    );
  },

  async createQuestion(data: CreateCommunityQuestion): Promise<CommunityQuestion> {
    return apiData<CommunityQuestion>('/api/v1/community/questions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};
