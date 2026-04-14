import { useEffect, useRef } from 'react';

import { api } from '@/api/client';
import type { ResearchEvent, Session } from '@/api/types';
import { useSessionStore } from '@/state/sessionStore';
import { ClarifyInput } from './ClarifyInput';
import { EventRenderer } from './EventRenderer';
import { FinalReport } from './FinalReport';
import { StatusBadge } from './StatusBadge';

interface ChatViewProps {
  session: Session;
  events: ResearchEvent[];
}

export function ChatView({ session, events }: ChatViewProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const stickToBottomRef = useRef(true);
  const upsertSession = useSessionStore((s) => s.upsertSession);
  const setActive = useSessionStore((s) => s.setActiveSession);

  useEffect(() => {
    stickToBottomRef.current = true;
  }, [session.id]);

  useEffect(() => {
    if (!stickToBottomRef.current) return;
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [events.length, session.status, session.final_report]);

  const handleScroll = () => {
    const el = scrollRef.current;
    if (!el) return;
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    stickToBottomRef.current = distanceFromBottom < 40;
  };

  const handleClarify = async (clarification: string) => {
    await api.clarify(session.id, clarification);
    // Optimistically flip status so UI hides the input immediately
    const updated = { ...session, status: 'active' as const, clarification_response: clarification };
    upsertSession(updated);
    setActive(updated);
  };

  return (
    <div className="flex h-full flex-col">
      <header className="flex items-center justify-between border-b border-neutral-800 px-6 py-3">
        <div className="min-w-0">
          <div className="truncate text-sm font-medium text-neutral-100">
            {session.initial_query}
          </div>
          <div className="mt-1 flex items-center gap-2 text-xs text-neutral-500">
            <StatusBadge status={session.status} />
            <span>thread {session.thread_id.slice(0, 8)}…</span>
          </div>
        </div>
      </header>

      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="scrollbar-thin flex-1 overflow-y-auto px-6 py-4"
      >
        {events.length === 0 && session.status === 'created' && (
          <div className="mt-20 text-center text-sm text-neutral-500">
            Waiting for research to start…
          </div>
        )}

        {events.map((ev, i) => (
          <EventRenderer key={`${ev.timestamp}-${i}`} event={ev} />
        ))}

        {session.status === 'clarification_needed' && (
          <ClarifyInput onSubmit={handleClarify} />
        )}

        {session.status === 'completed' && session.final_report && (
          <FinalReport markdown={session.final_report} filenameHint={session.initial_query} />
        )}

        {session.status === 'failed' && (
          <div className="my-4 rounded-lg border border-red-700 bg-red-950/30 p-4 text-sm text-red-300">
            ⚠️ Research failed. Check the server logs for details.
          </div>
        )}
      </div>
    </div>
  );
}
