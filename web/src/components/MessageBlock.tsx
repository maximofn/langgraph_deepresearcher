import { useEffect, useState, type MouseEvent, type ReactNode } from 'react';
import { ChevronDown } from 'lucide-react';
import type { AgentName, MessageKind, ResearchEvent } from '@/api/types';
import { useCollapseAll } from './CollapseAllContext';

interface BlockShellProps {
  color: string;
  cardBg: string;
  title: string;
  agent?: AgentName | null;
  children: ReactNode;
  copyText?: string;
  rightBadge?: string;
  defaultCollapsed?: boolean;
}

export function BlockShell({
  color,
  cardBg,
  title,
  agent,
  children,
  copyText,
  rightBadge,
  defaultCollapsed = false,
}: BlockShellProps) {
  const [collapsed, setCollapsed] = useState(defaultCollapsed);
  const [copied, setCopied] = useState(false);
  const collapseAll = useCollapseAll();
  useEffect(() => {
    if (!collapseAll || collapseAll.version === 0) return;
    setCollapsed(collapseAll.target);
  }, [collapseAll?.version, collapseAll?.target]);

  const handleCopy = async (e: MouseEvent) => {
    e.stopPropagation();
    if (!copyText) return;
    try {
      await navigator.clipboard.writeText(copyText);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {
      /* ignore */
    }
  };

  return (
    <div
      className={`mb-0.5 overflow-hidden rounded-[8px] border-l-[3px] ${
        collapsed ? 'cursor-pointer' : ''
      }`}
      style={{
        borderLeftColor: `${color}${collapsed ? '33' : '66'}`,
        backgroundColor: cardBg,
      }}
      onClick={collapsed ? () => setCollapsed(false) : undefined}
      role={collapsed ? 'button' : undefined}
    >
      <div
        className={`flex items-center gap-2.5 ${
          collapsed ? 'px-3.5 py-[10px]' : 'cursor-pointer px-4 pb-2.5 pt-[14px]'
        }`}
        onClick={!collapsed ? () => setCollapsed(true) : undefined}
      >
        <span
          className="inline-block h-2 w-2 shrink-0 rounded-full"
          style={{ backgroundColor: color }}
        />
        <span
          className="font-mono text-[11px] font-semibold uppercase tracking-wide"
          style={{ color }}
        >
          {title}
        </span>
        <div className="flex-1" />
        {agent && agent !== 'unknown' && AGENT_PILL[agent] && (
          <span
            className="rounded-[8px] px-2 py-[2px] font-mono text-[9px] font-medium"
            style={{
              backgroundColor: `${AGENT_PILL[agent].color}22`,
              color: AGENT_PILL[agent].color,
            }}
          >
            {AGENT_PILL[agent].label}
          </span>
        )}
        {rightBadge && (
          <span
            className="rounded-[8px] bg-[#1A1A1A] px-2 py-[2px] font-mono text-[9px] font-medium"
            style={{ color }}
          >
            {rightBadge}
          </span>
        )}
        {copyText && (
          <button
            type="button"
            onClick={handleCopy}
            className="font-mono text-[10px] text-[#444444] transition-colors hover:text-[#AAAAAA]"
          >
            {copied ? 'COPIED' : 'COPY'}
          </button>
        )}
        <button
          type="button"
          onClick={() => setCollapsed((c) => !c)}
          aria-label={collapsed ? 'Expand block' : 'Collapse block'}
          className="text-[#444444] transition-colors hover:text-[#AAAAAA]"
        >
          <ChevronDown
            size={14}
            className={`transition-transform ${collapsed ? '-rotate-90' : ''}`}
          />
        </button>
      </div>
      {!collapsed && (
        <div className="px-4 pb-[14px] font-sans text-[13px] leading-[1.4] text-[#CCCCCC]">
          {children}
        </div>
      )}
    </div>
  );
}

export const AGENT_PILL: Record<
  Exclude<AgentName, 'unknown'>,
  { label: string; color: string }
> = {
  scope: { label: 'Agent Scope', color: '#A855F7' },
  supervisor: { label: 'Agent Supervisor', color: '#0EA5E9' },
  research: { label: 'Agent Researcher', color: '#22C55E' },
  writer: { label: 'Agent Writer', color: '#F59E0B' },
};

export interface BlockStyle {
  color: string;
  cardBg: string;
  title: string;
}

export const BLOCK_CONFIG: Record<string, BlockStyle> = {
  Human: { color: '#00FF00', cardBg: '#0A150A', title: 'PRO' },
  AI: { color: '#00FF00', cardBg: '#0A150A', title: 'ASSISTANT' },
  ClarifyWithUser: { color: '#FF6B6B', cardBg: '#150A0A', title: 'CLARIFY WITH USER' },
  ResearchQuestion: { color: '#C084FC', cardBg: '#100A15', title: 'RESEARCH BRIEF' },
  Tool: { color: '#F472B6', cardBg: '#150A10', title: 'TOOL OUTPUT' },
  ToolCall: { color: '#06B6D4', cardBg: '#0A1215', title: 'TOOL CALL' },
  System: { color: '#FFB800', cardBg: '#15120A', title: 'SYSTEM' },
  Other: { color: '#6B8AFF', cardBg: '#0A0D15', title: 'MESSAGE' },
};

export function getBlockConfig(kind: MessageKind | null | undefined): BlockStyle {
  return BLOCK_CONFIG[kind || 'Other'] || BLOCK_CONFIG.Other;
}

export interface MessageBlockProps {
  event: ResearchEvent;
}
