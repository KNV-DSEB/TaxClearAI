import { HealthResponse } from '../types/api.types';

import { apiFetch } from './api.client';

export const healthService = {
  check: () => apiFetch<HealthResponse>('/health'),
};
