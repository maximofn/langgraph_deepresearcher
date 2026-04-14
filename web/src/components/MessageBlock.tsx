import { useState, type ReactNode } from 'react';
import type { AgentName, MessageKind, ResearchEvent } from '@/api/types';

interface BlockShellProps {
  color: string; // hex or tailwind bg value
  emoji: string;
  title: string;
  agent?: AgentName | null;
  children: ReactNode;
  defaultCollapsed?: boolean;
}

export function BlockShell({
  color,
  emoji,
  title,
  agent,
  children,
  defaultCollapsed = false,
}: BlockShellProps) {
  const [collapsed, setCollapsed] = useState(defaultCollapsed);
  return (
    <div
      className="my-2 rounded-md border-l-4 bg-neutral-900/40 px-4 py-3 shadow-sm"
      style={{ borderLeftColor: color, backgroundColor: `${color}0d` }}
    >
      <div className="flex items-center gap-2 text-xs uppercase tracking-wide">
        <span className="text-base">{emoji}</span>
        <span className="font-semibold" style={{ color }}>
          {title}
        </span>
        {agent && agent !== 'unknown' && (
          <span className="ml-auto rounded bg-neutral-800 px-2 py-0.5 text-[10px] font-medium text-neutral-400">
            {agent}
          </span>
        )}
        <button
          type="button"
          onClick={() => setCollapsed((c) => !c)}
          aria-label={collapsed ? 'Expand block' : 'Collapse block'}
          title={collapsed ? 'Expand' : 'Collapse'}
          className={`${agent && agent !== 'unknown' ? '' : 'ml-auto'} rounded p-1 text-neutral-400 hover:bg-neutral-800 hover:text-neutral-200 transition-colors`}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            className={`h-4 w-4 transition-transform ${collapsed ? '-rotate-90' : ''}`}
          >
            <path
              fillRule="evenodd"
              d="M5.23 7.21a.75.75 0 011.06.02L10 11.06l3.71-3.83a.75.75 0 111.08 1.04l-4.25 4.39a.75.75 0 01-1.08 0L5.21 8.27a.75.75 0 01.02-1.06z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>
      {!collapsed && (
        <div className="mt-1 text-sm text-neutral-200 whitespace-pre-wrap break-words">
          {children}
        </div>
      )}
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
