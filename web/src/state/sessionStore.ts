import { create } from 'zustand';
import type { ResearchEvent, Session } from '@/api/types';

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
}));
