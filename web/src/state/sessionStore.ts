import { create } from 'zustand';
import type {
  ApiKeysMap,
  ModelsCatalogResponse,
  ResearchEvent,
  Session,
} from '@/api/types';

const MODELS_STORAGE_KEY = 'deepresearch.models';
const API_KEYS_STORAGE_KEY = 'deepresearch.apikeys';
const USER_INFO_STORAGE_KEY = 'deepresearch.userinfo';

export interface UserInfo {
  name: string;
  email: string;
}

const EMPTY_USER_INFO: UserInfo = { name: '', email: '' };

// Stable empty reference to avoid the zustand selector gotcha documented in
// CLAUDE.md (inline `|| {}` creates a new object on every render).
const EMPTY_API_KEYS: ApiKeysMap = {};

function loadSelectedModelsFromStorage(): Record<string, string> {
  if (typeof window === 'undefined') return {};
  try {
    const raw = window.localStorage.getItem(MODELS_STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === 'object') return parsed as Record<string, string>;
    return {};
  } catch {
    return {};
  }
}

function persistSelectedModels(models: Record<string, string>): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(MODELS_STORAGE_KEY, JSON.stringify(models));
  } catch {
    /* ignore quota errors */
  }
}

function loadApiKeysFromStorage(): ApiKeysMap {
  if (typeof window === 'undefined') return EMPTY_API_KEYS;
  try {
    const raw = window.localStorage.getItem(API_KEYS_STORAGE_KEY);
    if (!raw) return EMPTY_API_KEYS;
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === 'object') return parsed as ApiKeysMap;
    return EMPTY_API_KEYS;
  } catch {
    return EMPTY_API_KEYS;
  }
}

function persistApiKeys(keys: ApiKeysMap): void {
  if (typeof window === 'undefined') return;
  try {
    if (Object.keys(keys).length === 0) {
      window.localStorage.removeItem(API_KEYS_STORAGE_KEY);
    } else {
      window.localStorage.setItem(API_KEYS_STORAGE_KEY, JSON.stringify(keys));
    }
  } catch {
    /* ignore quota errors */
  }
}

function loadUserInfoFromStorage(): UserInfo {
  if (typeof window === 'undefined') return EMPTY_USER_INFO;
  try {
    const raw = window.localStorage.getItem(USER_INFO_STORAGE_KEY);
    if (!raw) return EMPTY_USER_INFO;
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === 'object') {
      return {
        name: typeof parsed.name === 'string' ? parsed.name : '',
        email: typeof parsed.email === 'string' ? parsed.email : '',
      };
    }
    return EMPTY_USER_INFO;
  } catch {
    return EMPTY_USER_INFO;
  }
}

function persistUserInfo(info: UserInfo): void {
  if (typeof window === 'undefined') return;
  try {
    if (!info.name && !info.email) {
      window.localStorage.removeItem(USER_INFO_STORAGE_KEY);
    } else {
      window.localStorage.setItem(USER_INFO_STORAGE_KEY, JSON.stringify(info));
    }
  } catch {
    /* ignore quota errors */
  }
}

interface SessionState {
  // History
  sessions: Session[];
  setSessions: (s: Session[]) => void;
  upsertSession: (s: Session) => void;
  removeSession: (id: string) => void;

  // Active session
  activeSession: Session | null;
  setActiveSession: (s: Session | null) => void;

  // Events for the active session
  eventsBySession: Record<string, ResearchEvent[]>;
  appendEvent: (sessionId: string, ev: ResearchEvent) => void;
  setEvents: (sessionId: string, events: ResearchEvent[]) => void;
  clearEvents: (sessionId: string) => void;

  // Models catalog and per-role selection
  modelsCatalog: ModelsCatalogResponse | null;
  selectedModels: Record<string, string>;
  setModelsCatalog: (catalog: ModelsCatalogResponse) => void;
  setSelectedModels: (models: Record<string, string>) => void;

  // User-supplied API keys (localStorage-backed)
  apiKeys: ApiKeysMap;
  setApiKeys: (keys: ApiKeysMap) => void;

  // User contact info (name + email) used for final-report delivery
  userInfo: UserInfo;
  setUserInfo: (info: UserInfo) => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessions: [],
  setSessions: (sessions) => set({ sessions }),
  upsertSession: (s) =>
    set((state) => {
      const existing = state.sessions.find((x) => x.id === s.id);
      if (existing) {
        return {
          sessions: state.sessions.map((x) => (x.id === s.id ? s : x)),
        };
      }
      return { sessions: [s, ...state.sessions] };
    }),
  removeSession: (id) =>
    set((state) => ({
      sessions: state.sessions.filter((s) => s.id !== id),
      activeSession: state.activeSession?.id === id ? null : state.activeSession,
    })),

  activeSession: null,
  setActiveSession: (activeSession) => set({ activeSession }),

  eventsBySession: {},
  appendEvent: (sessionId, ev) =>
    set((state) => ({
      eventsBySession: {
        ...state.eventsBySession,
        [sessionId]: [...(state.eventsBySession[sessionId] || []), ev],
      },
    })),
  setEvents: (sessionId, events) =>
    set((state) => ({
      eventsBySession: {
        ...state.eventsBySession,
        [sessionId]: events,
      },
    })),
  clearEvents: (sessionId) =>
    set((state) => {
      const next = { ...state.eventsBySession };
      delete next[sessionId];
      return { eventsBySession: next };
    }),

  modelsCatalog: null,
  selectedModels: loadSelectedModelsFromStorage(),
  setModelsCatalog: (catalog) =>
    set((state) => {
      // If the user hasn't picked anything yet, seed from catalog defaults.
      const hasSelection = Object.keys(state.selectedModels).length > 0;
      const nextSelected = hasSelection ? state.selectedModels : { ...catalog.defaults };
      if (!hasSelection) persistSelectedModels(nextSelected);
      return { modelsCatalog: catalog, selectedModels: nextSelected };
    }),
  setSelectedModels: (models) => {
    persistSelectedModels(models);
    set({ selectedModels: models });
  },

  apiKeys: loadApiKeysFromStorage(),
  setApiKeys: (keys) => {
    persistApiKeys(keys);
    set({ apiKeys: keys });
  },

  userInfo: loadUserInfoFromStorage(),
  setUserInfo: (info) => {
    persistUserInfo(info);
    set({ userInfo: info });
  },
}));
