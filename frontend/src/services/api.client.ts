// The ONE place that reads the API base URL — see AGENTS.md "Frontend
// specifics". Every other file calls a service in this folder, never fetch
// directly from a component.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:3000';

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  });

  if (!res.ok) {
    throw new ApiError(res.status, `API request to ${path} failed with ${res.status}`);
  }

  return (await res.json()) as T;
}
