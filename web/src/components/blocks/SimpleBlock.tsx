import { BlockShell, getBlockConfig } from '@/components/MessageBlock';
import type { ResearchEvent } from '@/api/types';

/** Used for Human, AI, Clarify, Brief, Tool output (text), System, Other. */
export function SimpleBlock({ event }: { event: ResearchEvent }) {
  const cfg = getBlockConfig(event.message_type);
  const title = event.message_subtype === 'RealHumanMessage' ? 'YOU' : cfg.title;
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
