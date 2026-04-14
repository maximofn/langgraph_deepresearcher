import { BlockShell, getBlockConfig } from '@/components/MessageBlock';
import type { ResearchEvent } from '@/api/types';

export function ToolCallBlock({ event }: { event: ResearchEvent }) {
  const cfg = getBlockConfig('ToolCall');
  const name = event.tool_name || 'tool';
  const argsJson = JSON.stringify(event.tool_args || {}, null, 2);

  return (
    <BlockShell
      color={cfg.color}
      cardBg={cfg.cardBg}
      title={`TOOL CALL: ${name.toUpperCase()}`}
      agent={event.agent}
      copyText={argsJson}
    >
      <pre className="overflow-x-auto rounded-[6px] bg-[#080808] p-3 font-mono text-[12px] leading-[1.5] text-[#888888]">
        {argsJson}
      </pre>
      {event.tool_call_id && (
        <div className="mt-2 font-mono text-[10px] text-[#444444]">
          id: {event.tool_call_id}
        </div>
      )}
    </BlockShell>
  );
}
