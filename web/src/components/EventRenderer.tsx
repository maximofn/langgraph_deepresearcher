import type { ResearchEvent } from '@/api/types';
import { SimpleBlock } from './blocks/SimpleBlock';
import { ToolCallBlock } from './blocks/ToolCallBlock';
import { ToolOutputBlock } from './blocks/ToolOutputBlock';

export function EventRenderer({ event }: { event: ResearchEvent }) {
  switch (event.message_type) {
    case 'ToolCall':
      return <ToolCallBlock event={event} />;
    case 'Tool':
      return <ToolOutputBlock event={event} />;
    case 'Human':
    case 'AI':
    case 'ClarifyWithUser':
    case 'ResearchQuestion':
    case 'System':
    case 'Other':
    default:
      return <SimpleBlock event={event} />;
  }
}
