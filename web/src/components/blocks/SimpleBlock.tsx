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
  const content = event.content || '';
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
