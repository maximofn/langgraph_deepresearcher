import { BlockShell, getBlockConfig } from '@/components/MessageBlock';
import type { ResearchEvent } from '@/api/types';

/**
 * Formats tool args in a readable pseudo-JSON style:
 * - Keys without quotes
 * - String values with actual newlines (not escaped)
 * - Multi-line strings open/close with " on their own lines
 */
function formatToolArgs(args: Record<string, unknown>): string {
  const entries = Object.entries(args);
  if (entries.length === 0) return '{}';

  const lines: string[] = ['{'];
  for (const [key, value] of entries) {
    if (typeof value === 'string') {
      if (value.includes('\n')) {
        lines.push(`  ${key}: "`);
        for (const line of value.split('\n')) {
          lines.push(`  ${line}`);
        }
        lines.push('  "');
      } else {
        lines.push(`  ${key}: "${value}"`);
      }
    } else {
      lines.push(`  ${key}: ${JSON.stringify(value, null, 2)}`);
    }
  }
  lines.push('}');
  return lines.join('\n');
}

export function ToolCallBlock({ event }: { event: ResearchEvent }) {
  const cfg = getBlockConfig('ToolCall');
  const name = event.tool_name || 'tool';
  const argsJson = formatToolArgs(event.tool_args || {});

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
