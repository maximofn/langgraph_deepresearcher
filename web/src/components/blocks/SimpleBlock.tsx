import { BlockShell, getBlockConfig } from '@/components/MessageBlock';
import type { ResearchEvent } from '@/api/types';

/** Used for Human, AI, Clarify, Brief, Tool output (text), System, Other. */
export function SimpleBlock({ event }: { event: ResearchEvent }) {
  const cfg = getBlockConfig(event.message_type);
  const title = event.message_subtype === 'RealHumanMessage' ? 'You' : cfg.title;
  return (
    <BlockShell color={cfg.color} emoji={cfg.emoji} title={title} agent={event.agent}>
      {event.content}
    </BlockShell>
  );
}
