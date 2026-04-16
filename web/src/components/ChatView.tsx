import { useEffect, useRef, useState } from 'react';
import { ChevronsDownUp, ChevronsUpDown, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { api } from '@/api/client';
import { markdownComponents } from './markdownComponents';
import type { ResearchEvent, Session } from '@/api/types';
import { useSessionStore } from '@/state/sessionStore';
import { ClarifyInput } from './ClarifyInput';
import { PostResearchChat } from './PostResearchChat';
import { CollapseAllProvider, useCollapseAll } from './CollapseAllContext';
import { EventRenderer } from './EventRenderer';
import { FinalReport } from './FinalReport';
import { StatusBadge } from './StatusBadge';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

function CollapseAllButtons() {
  const ctx = useCollapseAll();
  if (!ctx) return null;
  const collapseActive = ctx.allCollapsed;
  const expandActive = ctx.allExpanded;
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
  const apiKeys = useSessionStore((s) => s.apiKeys);

  // Local chat conversation history (user messages + assistant responses)
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  // Track how many chat_response events we've already processed (avoid duplicates)
  const processedChatResponsesRef = useRef(0);

  const [isChatting, setIsChatting] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);

  useEffect(() => {
    stickToBottomRef.current = true;
  }, [session.id]);

  useEffect(() => {
    if (!stickToBottomRef.current) return;
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [events.length, session.status, session.final_report, chatMessages.length]);

  // Watch for incoming chat_response events and add them to the chat history
  useEffect(() => {
    const chatResponseEvents = events.filter((e) => e.event_type === 'chat_response');
    const newEvents = chatResponseEvents.slice(processedChatResponsesRef.current);
    if (newEvents.length === 0) return;

    processedChatResponsesRef.current = chatResponseEvents.length;
    setChatMessages((prev) => [
      ...prev,
      ...newEvents.map((e) => ({ role: 'assistant' as const, content: e.content })),
    ]);
  }, [events]);

  const handleScroll = () => {
    const el = scrollRef.current;
    if (!el) return;
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    stickToBottomRef.current = distanceFromBottom < 40;
  };

  const handleClarify = async (clarification: string) => {
    const nonEmpty = Object.fromEntries(
      Object.entries(apiKeys).filter(([, v]) => v && v.trim().length > 0),
    );
    await api.clarify(
      session.id,
      clarification,
      Object.keys(nonEmpty).length > 0 ? nonEmpty : undefined,
    );
    const updated = {
      ...session,
      status: 'active' as const,
      clarification_response: clarification,
    };
    upsertSession(updated);
    setActive(updated);
  };

  const handleChat = async (message: string) => {
    setChatError(null);
    setIsChatting(true);
    // Optimistically add the user message to the local chat history
    setChatMessages((prev) => [...prev, { role: 'user', content: message }]);
    try {
      await api.chat(session.id, message);
    } catch (err) {
      const msg = err && typeof err === 'object' && 'message' in err
        ? String((err as { message: unknown }).message)
        : 'Failed to send message. Please try again.';
      setChatError(msg);
      // Remove the optimistic user message on error
      setChatMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsChatting(false);
    }
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
          className="scrollbar-thin flex-1 overflow-y-auto"
        >
          <div className="flex min-h-full flex-col justify-end px-6 py-4">
          {events.length === 0 && session.status === 'created' && (
            <div className="text-center font-sans text-sm text-[#555555]">
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
            <>
              <FinalReport
                markdown={session.final_report}
                filenameHint={session.initial_query}
              />

              {/* Post-research chat conversation */}
              {chatMessages.map((msg, i) =>
                msg.role === 'user' ? (
                  /* YOU block — same style as YouBlock.tsx */
                  <div key={i} className="flex w-full flex-col gap-[6px] px-1 py-2">
                    <div className="flex items-center justify-end gap-2">
                      <span
                        className="font-mono text-[11px] font-semibold uppercase tracking-wide"
                        style={{ color: '#00FF00' }}
                      >
                        YOU
                      </span>
                      <span
                        className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full"
                        style={{ backgroundColor: '#00FF0015' }}
                      >
                        <User size={10} color="#00FF00" />
                      </span>
                    </div>
                    <div className="whitespace-pre-wrap break-words text-right font-sans text-[13px] leading-[1.4] text-[#CCCCCC]">
                      {msg.content}
                    </div>
                  </div>
                ) : (
                  /* WRITER response block */
                  <div
                    key={i}
                    className="my-3 rounded-[8px] border-l-[3px] px-4 py-3 font-sans text-[13px] text-terminal-textPrimary"
                    style={{ borderLeftColor: '#4FC3F7AA', backgroundColor: '#0A0F15' }}
                  >
                    <div className="mb-1.5 font-mono text-[10px] font-semibold uppercase tracking-wide text-[#4FC3F7]">
                      Deep Researcher
                    </div>
                    <div className="markdown-body">
                      <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>{msg.content}</ReactMarkdown>
                    </div>
                  </div>
                ),
              )}

              {isChatting && (
                <div className="my-3 flex items-center gap-2 px-4 py-3 font-mono text-[11px] text-[#4FC3F7]">
                  <span className="animate-pulse">●</span>
                  <span>Writer is thinking…</span>
                </div>
              )}

              {chatError && (
                <div
                  className="my-3 rounded-[8px] border-l-[3px] px-4 py-3 font-sans text-[13px] text-[#FF6B6B]"
                  style={{ borderLeftColor: '#FF6B6B66', backgroundColor: '#150A0A' }}
                >
                  {chatError}
                </div>
              )}

              <PostResearchChat onSubmit={handleChat} disabled={isChatting} />
            </>
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
      </div>
    </CollapseAllProvider>
  );
}
