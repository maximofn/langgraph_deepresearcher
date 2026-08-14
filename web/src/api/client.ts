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

/**
 * Error thrown by every failed API call.
 *
 * It extends `Error` on purpose: callers do `err instanceof Error ? err.message
 * : <fallback>`, and a plain object silently loses to the fallback — which used
 * to hide the backend's own explanation ("Missing API keys: ...") behind a
 * generic message at the exact moment the user needs to read it.
 */
export class ApiRequestError extends Error {
  code: string;
  status: number;
  details?: Record<string, unknown> | null;

  constructor(status: number, body: unknown, fallback: string) {
    const payload = (body ?? {}) as Partial<ApiError> & { detail?: unknown };
    // Two shapes reach us: {code, message, details} from the app's own handlers,
    // and {detail} from raw FastAPI HTTPExceptions.
    const detailText =
      typeof payload.detail === 'string' ? payload.detail : undefined;
    super(payload.message || detailText || fallback);
    this.name = 'ApiRequestError';
    this.status = status;
    this.code = payload.code || 'http_error';
    this.details =
      payload.details ??
      (payload.detail && typeof payload.detail === 'object'
        ? (payload.detail as Record<string, unknown>)
        : undefined);
  }
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
    let body: unknown = null;
    try {
      body = await res.json();
    } catch {
      // Non-JSON response (proxy error, 502 HTML page…) — fall back below.
    }
    throw new ApiRequestError(res.status, body, `${res.status} ${res.statusText}`);
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

  // The writer needs credentials on every follow-up turn too — the backend has
  // none of its own in production.
  chat: (id: string, message: string, apiKeys?: Record<string, string>) =>
    request<StartResearchResponse>(`/sessions/${id}/chat`, {
      method: 'POST',
      body: JSON.stringify({
        message,
        ...(apiKeys && Object.keys(apiKeys).length > 0 ? { api_keys: apiKeys } : {}),
      } satisfies ChatSessionRequest),
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
