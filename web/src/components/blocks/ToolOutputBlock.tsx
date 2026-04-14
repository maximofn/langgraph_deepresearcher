import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';

import { BlockShell, getBlockConfig } from '@/components/MessageBlock';
import type { ResearchEvent } from '@/api/types';

const PREVIEW_CHARS = 400;

export function ToolOutputBlock({ event }: { event: ResearchEvent }) {
  const [open, setOpen] = useState(false);
  const cfg = getBlockConfig('Tool');
  const content = event.content || '';
  const isLong = content.length > PREVIEW_CHARS;
  const preview = isLong && !open ? content.slice(0, PREVIEW_CHARS) + '…' : content;

  const name = event.tool_name ? `Tool Output: ${event.tool_name}` : cfg.title;

  return (
    <BlockShell color={cfg.color} emoji={cfg.emoji} title={name} agent={event.agent}>
      <div className="font-mono text-xs leading-relaxed">{preview}</div>
      {isLong && (
        <button
          onClick={() => setOpen(!open)}
          className="mt-2 flex items-center gap-1 text-xs text-neutral-400 hover:text-neutral-200"
        >
          {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          {open ? 'Collapse' : `Expand (${content.length} chars)`}
        </button>
      )}
    </BlockShell>
  );
}
