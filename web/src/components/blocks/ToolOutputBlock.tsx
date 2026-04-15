import { useState } from 'react';

import { BlockShell, getBlockConfig } from '@/components/MessageBlock';
import type { ResearchEvent } from '@/api/types';

const PREVIEW_CHARS = 400;

export function ToolOutputBlock({ event }: { event: ResearchEvent }) {
  const [open, setOpen] = useState(false);
  const cfg = getBlockConfig('Tool');
  const content = event.content || '';
  const isLong = content.length > PREVIEW_CHARS;
  const preview = isLong && !open ? content.slice(0, PREVIEW_CHARS) + '…' : content;
  const name = event.tool_name
    ? `TOOL OUTPUT: ${event.tool_name.toUpperCase()}`
    : cfg.title;

  return (
    <BlockShell
      color={cfg.color}
      cardBg={cfg.cardBg}
      title={name}
      agent={event.agent}
      copyText={content}
    >
      <pre className="overflow-x-auto whitespace-pre-wrap break-words rounded-[6px] bg-[#080808] p-3 font-mono text-[12px] leading-[1.5] text-[#888888]">
        {preview}
      </pre>
      {isLong && (
        <button
          type="button"
          onClick={() => setOpen((o) => !o)}
          className="mt-2 font-mono text-[11px] text-[#00FF00] hover:brightness-125"
        >
          {open ? 'Show less' : `Expand (${content.length} chars)`}
        </button>
      )}
    </BlockShell>
  );
}
