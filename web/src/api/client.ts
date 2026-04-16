import type {
  ApiError,
  ApiKeysMap,
  ChatSessionRequest,
  CreateSessionRequest,
  CreateSessionResponse,
  ModelsCatalogResponse,
  PersistedMessage,
  Session,
  SessionListResponse,
  StartResearchResponse,
} from './types';

const API_BASE = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '');

const CLIENT_ID_KEY = 'deepresearch.client_id';

function getOrCreateClientId(): string {
  let id = window.localStorage.getItem(CLIENT_ID_KEY);
  if (!id) {
    id = crypto.randomUUID();
    try {
      window.localStorage.setItem(CLIENT_ID_KEY, id);
    } catch {
      // localStorage not available — id won't persist across page loads
    }
  }
  return id;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      'X-Client-ID': getOrCreateClientId(),
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

  clarify: (id: string, clarification: string, apiKeys?: Record<string, string>) =>
    request<StartResearchResponse>(`/sessions/${id}/clarify`, {
      method: 'POST',
      body: JSON.stringify({
        clarification,
        ...(apiKeys && Object.keys(apiKeys).length > 0 ? { api_keys: apiKeys } : {}),
      }),
    }),

  chat: (id: string, message: string) =>
    request<StartResearchResponse>(`/sessions/${id}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message } satisfies ChatSessionRequest),
    }),

  deleteSession: (id: string) =>
    request<void>(`/sessions/${id}`, { method: 'DELETE' }),

  getModels: () => request<ModelsCatalogResponse>('/models/'),

  discoverModels: (apiKeys: ApiKeysMap) =>
    request<ModelsCatalogResponse>('/models/discover', {
      method: 'POST',
      body: JSON.stringify({ api_keys: apiKeys }),
    }),
};
