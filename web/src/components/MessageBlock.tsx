import type { ReactNode } from 'react';
import type { AgentName, MessageKind, ResearchEvent } from '@/api/types';

interface BlockShellProps {
  color: string; // hex or tailwind bg value
  emoji: string;
  title: string;
  agent?: AgentName | null;
  children: ReactNode;
}

export function BlockShell({ color, emoji, title, agent, children }: BlockShellProps) {
  return (
    <div
      className="my-2 rounded-md border-l-4 bg-neutral-900/40 px-4 py-3 shadow-sm"
      style={{ borderLeftColor: color, backgroundColor: `${color}0d` }}
    >
      <div className="mb-1 flex items-center gap-2 text-xs uppercase tracking-wide">
        <span className="text-base">{emoji}</span>
        <span className="font-semibold" style={{ color }}>
          {title}
        </span>
        {agent && agent !== 'unknown' && (
          <span className="ml-auto rounded bg-neutral-800 px-2 py-0.5 text-[10px] font-medium text-neutral-400">
            {agent}
          </span>
        )}
      </div>
      <div className="text-sm text-neutral-200 whitespace-pre-wrap break-words">
        {children}
      </div>
    </div>
  );
}

export const BLOCK_CONFIG: Record<
  string,
  { color: string; emoji: string; title: string }
> = {
  Human: { color: '#201ADB', emoji: '🧑', title: 'User' },
  AI: { color: '#24FA00', emoji: '🤖', title: 'Assistant' },
  ClarifyWithUser: { color: '#37DB1A', emoji: '❓', title: 'Clarify With User' },
  ResearchQuestion: { color: '#37DB1A', emoji: '📋', title: 'Research Brief' },
  Tool: { color: '#EAB308', emoji: '📤', title: 'Tool Output' },
  ToolCall: { color: '#C026D3', emoji: '🔧', title: 'Tool Call' },
  System: { color: '#EF4444', emoji: '⚙️', title: 'System' },
  Other: { color: '#A3A3A3', emoji: '📝', title: 'Message' },
};

export function getBlockConfig(kind: MessageKind | null | undefined) {
  return BLOCK_CONFIG[kind || 'Other'] || BLOCK_CONFIG.Other;
}

export interface MessageBlockProps {
  event: ResearchEvent;
}
