// The ONE place that reads the API base URL — see AGENTS.md "Frontend
// specifics". Every other file calls a service in this folder, never fetch
// directly from a component.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

let refreshRequest: Promise<boolean> | null = null;

async function refreshSession(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/refreshes`, {
      method: 'POST',
      credentials: 'include',
      signal: AbortSignal.timeout(10000),
    });
    return response.ok;
  } catch {
    return false;
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const options: RequestInit = {
    ...init,
    credentials: 'include',
    signal: init?.signal ?? AbortSignal.timeout(25000),
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  };
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, options);
    if (response.status === 401 && !path.startsWith('/api/v1/auth/')) {
      refreshRequest ??= refreshSession();
      const refreshed = await refreshRequest;
      refreshRequest = null;
      if (refreshed) response = await fetch(`${API_BASE_URL}${path}`, options);
    }
  } catch (error) {
    if (init?.signal?.aborted) throw error;
    throw new ApiError(0, 'Chưa kết nối được. Vui lòng kiểm tra kết nối và thử lại.');
  }
  if (!response.ok) {
    const problem: { detail?: string } = await response.json().catch(() => ({}));
    throw new ApiError(
      response.status,
      problem.detail ?? 'Chưa xử lý được yêu cầu. Vui lòng thử lại.',
    );
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function apiData<T>(path: string, init?: RequestInit): Promise<T> {
  return (await apiFetch<{ data: T }>(path, init)).data;
}
