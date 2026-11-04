import type { LegalCategory, LegalDocument, LegalDocumentList } from '@/types/legal.types';

import { apiData } from './api.client';

export const legalService = {
  getDocuments(
    query: string,
    category: LegalCategory | '',
    signal?: AbortSignal,
  ): Promise<LegalDocumentList> {
    const params = new URLSearchParams();
    if (query.trim()) params.set('q', query.trim());
    if (category) params.set('category', category);
    return apiData<LegalDocumentList>(`/api/v1/legal/?${params.toString()}`, { signal });
  },

  getDocument(slug: string, signal?: AbortSignal): Promise<LegalDocument> {
    return apiData<LegalDocument>(`/api/v1/legal/${encodeURIComponent(slug)}`, { signal });
  },
};
