import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';

import { BlockShell, getBlockConfig } from '@/components/MessageBlock';
import type { ResearchEvent } from '@/api/types';

export function ToolCallBlock({ event }: { event: ResearchEvent }) {
  const [open, setOpen] = useState(true);
  const cfg = getBlockConfig('ToolCall');
  const name = event.tool_name || 'tool';
  const args = event.tool_args;

  return (
    <BlockShell
      color={cfg.color}
      emoji={cfg.emoji}
      title={`Tool Call: ${name}`}
      agent={event.agent}
    >
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1 text-xs text-neutral-400 hover:text-neutral-200"
      >
        {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        Arguments
      </button>
      {open && (
        <pre className="mt-2 overflow-x-auto rounded bg-neutral-900 p-3 font-mono text-xs text-neutral-300">
          {JSON.stringify(args || {}, null, 2)}
        </pre>
      )}
      {event.tool_call_id && (
        <div className="mt-1 font-mono text-[10px] text-neutral-500">
          id: {event.tool_call_id}
        </div>
      )}
    </BlockShell>
  );
}
