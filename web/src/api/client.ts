import type {
  ApiError,
  CreateSessionRequest,
  CreateSessionResponse,
  PersistedMessage,
  Session,
  SessionListResponse,
  StartResearchResponse,
} from './types';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    let err: ApiError;
    try {
      err = (await res.json()) as ApiError;
    } catch {
      err = { code: 'http_error', message: `${res.status} ${res.statusText}` };
    }
    throw err;
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  listSessions: (limit = 50, offset = 0) =>
    request<SessionListResponse>(`/sessions/?limit=${limit}&offset=${offset}`),

  getSession: (id: string) => request<Session>(`/sessions/${id}`),

  getMessages: (id: string) => request<PersistedMessage[]>(`/sessions/${id}/messages`),

  createSession: (body: CreateSessionRequest) =>
    request<CreateSessionResponse>('/sessions/', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  startResearch: (id: string) =>
    request<StartResearchResponse>(`/sessions/${id}/start`, { method: 'POST' }),

  clarify: (id: string, clarification: string) =>
    request<StartResearchResponse>(`/sessions/${id}/clarify`, {
      method: 'POST',
      body: JSON.stringify({ clarification }),
    }),

  deleteSession: (id: string) =>
    request<void>(`/sessions/${id}`, { method: 'DELETE' }),
};
