import { useEffect, useRef } from 'react';
import { ChevronsDownUp, ChevronsUpDown } from 'lucide-react';

import { api } from '@/api/client';
import type { ResearchEvent, Session } from '@/api/types';
import { useSessionStore } from '@/state/sessionStore';
import { ClarifyInput } from './ClarifyInput';
import { CollapseAllProvider, useCollapseAll } from './CollapseAllContext';
import { EventRenderer } from './EventRenderer';
import { FinalReport } from './FinalReport';
import { StatusBadge } from './StatusBadge';

function CollapseAllButtons() {
  const ctx = useCollapseAll();
  if (!ctx) return null;
  const active = ctx.version > 0 ? ctx.target : null;
  const collapseActive = active === true;
  const expandActive = active === false;
  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={ctx.collapseAll}
        title="Collapse all"
        aria-label="Collapse all blocks"
        className={`flex items-center gap-1.5 rounded-[6px] px-2.5 py-1.5 font-sans text-[12px] transition-colors ${
          collapseActive
            ? 'border border-[#00FF0025] bg-[#00FF0010] text-[#00FF00]'
            : 'text-[#666666] hover:text-[#CCCCCC]'
        }`}
      >
        <ChevronsDownUp size={14} />
        <span>Collapse all</span>
      </button>
      <button
        type="button"
        onClick={ctx.expandAll}
        title="Expand all"
        aria-label="Expand all blocks"
        className={`flex items-center gap-1.5 rounded-[6px] px-2.5 py-1.5 font-sans text-[12px] transition-colors ${
          expandActive
            ? 'border border-[#00FF0025] bg-[#00FF0010] text-[#00FF00]'
            : 'text-[#666666] hover:text-[#CCCCCC]'
        }`}
      >
        <ChevronsUpDown size={14} />
        <span>Expand all</span>
      </button>
    </div>
  );
}

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
    const updated = {
      ...session,
      status: 'active' as const,
      clarification_response: clarification,
    };
    upsertSession(updated);
    setActive(updated);
  };

  return (
    <CollapseAllProvider>
      <div className="flex h-full flex-col bg-terminal-bg">
        <header className="flex items-center justify-between gap-4 border-b border-[#1A1A1A] bg-[#0D0D0D] px-6 py-4">
          <div className="flex min-w-0 items-center gap-3">
            <div className="truncate font-sans text-[16px] font-medium leading-[1.3] text-white">
              {session.initial_query}
            </div>
            <StatusBadge status={session.status} />
          </div>
          <CollapseAllButtons />
        </header>

        <div
          ref={scrollRef}
          onScroll={handleScroll}
          className="scrollbar-thin flex-1 overflow-y-auto px-6 py-4"
        >
          {events.length === 0 && session.status === 'created' && (
            <div className="mt-20 text-center font-sans text-sm text-[#555555]">
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
            <FinalReport
              markdown={session.final_report}
              filenameHint={session.initial_query}
            />
          )}

          {session.status === 'failed' && (
            <div
              className="my-4 rounded-[8px] border-l-[3px] px-4 py-3 font-sans text-[13px] text-[#FF6B6B]"
              style={{ borderLeftColor: '#FF6B6B66', backgroundColor: '#150A0A' }}
            >
              Research failed. Check the server logs for details.
            </div>
          )}
        </div>
      </div>
    </CollapseAllProvider>
  );
}
