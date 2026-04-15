import { BlockShell, getBlockConfig } from '@/components/MessageBlock';
import type { ResearchEvent } from '@/api/types';
import { YouBlock } from './YouBlock';

/** Used for Human, AI, Clarify, Brief, Tool output (text), System, Other. */
export function SimpleBlock({ event }: { event: ResearchEvent }) {
  if (event.message_subtype === 'RealHumanMessage') {
    return <YouBlock event={event} />;
  }
  const cfg = getBlockConfig(event.message_type);
  const title = cfg.title;
  const raw = event.content || '';
  // Strip the research_brief='...' wrapper produced by the scope agent
  let content =
    event.message_type === 'ResearchQuestion'
      ? (raw.match(/^research_brief='([\s\S]*)'\s*$/)?.[1] ?? raw)
      : raw;

  // Truncate supervisor end-of-loop System messages after "Research iterations: N"
  if (event.message_type === 'System') {
    const match = content.match(/(.*?Research iterations:\s*\d+)/s);
    if (match) content = match[1];
  }
  return (
    <BlockShell
      color={cfg.color}
      cardBg={cfg.cardBg}
      title={title}
      agent={event.agent}
      copyText={content}
    >
      <div className="whitespace-pre-wrap break-words">{content}</div>
    </BlockShell>
  );
}
