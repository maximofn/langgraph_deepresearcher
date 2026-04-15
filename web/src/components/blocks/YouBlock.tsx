import { useEffect, useState, type MouseEvent } from 'react';
import { Check, ChevronDown, Copy, User } from 'lucide-react';
import type { ResearchEvent } from '@/api/types';
import { useCollapseAll } from '@/components/CollapseAllContext';

/**
 * Differentiated "YOU" block for real user messages.
 *
 * Mirror-inverted layout vs agent blocks:
 *  - Border on the RIGHT (not left)
 *  - Header order reversed: [Copy] ← [YOU label] [Avatar]
 *  - Content right-aligned
 *  - No agent tag
 */
export function YouBlock({ event }: { event: ResearchEvent }) {
  const content = event.content || '';
  const [collapsed, setCollapsed] = useState(false);
  const [copied, setCopied] = useState(false);
  const collapseAll = useCollapseAll();

  useEffect(() => {
    if (!collapseAll || collapseAll.version === 0) return;
    setCollapsed(collapseAll.target);
  }, [collapseAll?.version, collapseAll?.target]);

  const handleCopy = async (e: MouseEvent) => {
    e.stopPropagation();
    if (!content) return;
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {
      /* ignore */
    }
  };

  const borderColor = '#00FF00';
  const bg = '#00FF0003';

  return (
    <div
      className={`mb-0.5 overflow-hidden rounded-[10px] border-r-[3px] ${
        collapsed ? 'cursor-pointer' : ''
      }`}
      style={{
        borderRightColor: `${borderColor}${collapsed ? '33' : '66'}`,
        backgroundColor: bg,
      }}
      onClick={collapsed ? () => setCollapsed(false) : undefined}
      role={collapsed ? 'button' : undefined}
    >
      <div
        className={`flex items-center gap-2.5 ${
          collapsed ? 'py-[10px] pl-[14px] pr-[14px]' : 'cursor-pointer pb-2.5 pl-[18px] pr-[18px] pt-4'
        }`}
        onClick={!collapsed ? () => setCollapsed(true) : undefined}
      >
        {/* Copy button — LEFT (opposite of agent blocks) */}
        <button
          type="button"
          onClick={handleCopy}
          className={`group inline-flex items-center gap-1 rounded-[6px] border px-[10px] py-[4px] font-mono text-[10px] transition-colors ${
            copied
              ? 'border-[#00FF00] text-[#00FF00]'
              : 'border-[#444444] bg-transparent text-[#888888] hover:border-[#666666] hover:bg-[#1A1A1A] hover:text-[#AAAAAA] active:border-[#00FF00] active:text-[#00FF00]'
          }`}
        >
          {copied ? <Check size={11} /> : <Copy size={11} />}
          <span>{copied ? 'Copied!' : 'Copy'}</span>
        </button>

        <div className="flex-1" />

        {/* YOU label */}
        <span
          className="font-mono text-[11px] font-semibold uppercase tracking-wide"
          style={{ color: '#00FF00' }}
        >
          YOU
        </span>

        {/* User avatar — replaces the dot of agent blocks */}
        <span
          className="flex h-[18px] w-[18px] shrink-0 items-center justify-center rounded-full"
          style={{ backgroundColor: '#00FF0015' }}
        >
          <User size={10} color="#00FF00" />
        </span>

        {/* Expand/Collapse control — far right */}
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            setCollapsed((c) => !c);
          }}
          aria-label={collapsed ? 'Expand block' : 'Collapse block'}
          className="flex items-center gap-1 text-[#444444] transition-colors hover:text-[#AAAAAA]"
        >
          <span className="font-mono text-[10px] uppercase">
            {collapsed ? 'Expand' : 'Collapse'}
          </span>
          <ChevronDown
            size={14}
            className={`transition-transform ${collapsed ? '-rotate-90' : ''}`}
          />
        </button>
      </div>

      {!collapsed && (
        <div className="pb-[16px] pl-[18px] pr-[18px] text-right font-sans text-[13px] leading-[1.4] text-[#CCCCCC]">
          <div className="whitespace-pre-wrap break-words">{content}</div>
        </div>
      )}
    </div>
  );
}
