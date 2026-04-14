import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

import { api } from '@/api/client';
import type { ResearchEvent } from '@/api/types';
import { useWebSocket } from '@/api/websocket';
import { ChatView } from '@/components/ChatView';
import { useSessionStore } from '@/state/sessionStore';

const EMPTY_EVENTS: ResearchEvent[] = [];

export function SessionPage() {
  const { id } = useParams<{ id: string }>();
  const session = useSessionStore((s) =>
    id ? s.sessions.find((x) => x.id === id) || null : null
  );
  const upsertSession = useSessionStore((s) => s.upsertSession);
  const setActiveSession = useSessionStore((s) => s.setActiveSession);
  const events = useSessionStore((s) => (id && s.eventsBySession[id]) || EMPTY_EVENTS);
  const appendEvent = useSessionStore((s) => s.appendEvent);

  const [error, setError] = useState<string | null>(null);

  // Fetch session details on mount / id change
  useEffect(() => {
    if (!id) return;
    (async () => {
      try {
        const s = await api.getSession(id);
        upsertSession(s);
        setActiveSession(s);
      } catch (err) {
        console.error(err);
        setError('Session not found');
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  // Poll session status while active (WebSocket doesn't push status changes)
  useEffect(() => {
    if (!id || !session) return;
    if (session.status !== 'active' && session.status !== 'clarification_needed') return;
    const interval = setInterval(async () => {
      try {
        const s = await api.getSession(id);
        upsertSession(s);
        setActiveSession(s);
        if (s.status === 'completed' || s.status === 'failed') {
          clearInterval(interval);
        }
      } catch {
        /* ignore */
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [id, session?.status, upsertSession, setActiveSession]);

  const handleEvent = useCallback(
    (ev: ResearchEvent) => {
      if (id) appendEvent(id, ev);
    },
    [id, appendEvent]
  );

  const enabled =
    !!session &&
    (session.status === 'active' ||
      session.status === 'created' ||
      session.status === 'clarification_needed');

  useWebSocket({ sessionId: enabled ? id || null : null, onEvent: handleEvent });

  if (error) {
    return <div className="p-10 text-center text-neutral-400">{error}</div>;
  }
  if (!session) {
    return <div className="p-10 text-center text-neutral-500">Loading…</div>;
  }
  return <ChatView session={session} events={events} />;
}
