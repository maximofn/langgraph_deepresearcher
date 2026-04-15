import type { ResearchEvent } from '@/api/types';
import { ClarifyWithUserBlock } from './blocks/ClarifyWithUserBlock';
import { SimpleBlock } from './blocks/SimpleBlock';
import { ToolCallBlock } from './blocks/ToolCallBlock';
import { ToolOutputBlock } from './blocks/ToolOutputBlock';

export function EventRenderer({ event }: { event: ResearchEvent }) {
  // Skip internal session lifecycle events — they are backend plumbing and the
  // YOU block already shows the user's query, making these redundant.
  if (event.event_type === 'session_created' || event.event_type === 'session_started') {
    return null;
  }

  switch (event.message_type) {
    case 'ToolCall':
      return <ToolCallBlock event={event} />;
    case 'Tool':
      return <ToolOutputBlock event={event} />;
    case 'ClarifyWithUser':
      return <ClarifyWithUserBlock event={event} />;
    case 'Human':
    case 'AI':
    case 'ResearchQuestion':
    case 'System':
    case 'Other':
    default:
      return <SimpleBlock event={event} />;
  }
}
