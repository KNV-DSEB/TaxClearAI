import { apiData, apiFetch } from './api.client';

interface Session {
  user: { id: string; username: string };
  expiresAt: string;
}

export const authService = {
  async login(username: string, password: string): Promise<Session> {
    return apiData<Session>('/api/v1/auth/sessions', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  },
  async current(signal?: AbortSignal): Promise<Session['user']> {
    return apiData<Session['user']>('/api/v1/auth/sessions/current', { signal });
  },
  async logout(): Promise<void> {
    await apiFetch<void>('/api/v1/auth/sessions/current', { method: 'DELETE' });
  },
};
