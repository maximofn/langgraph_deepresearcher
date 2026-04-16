import { User } from 'lucide-react';
import type { ResearchEvent } from '@/api/types';

/**
 * "YOU" block for real user messages.
 *
 * Mirror-inverted design: strips all card styling (no background, no border,
 * no rounded corners, no collapse, no copy button) to differentiate user
 * messages from agent/system blocks. Right-aligned.
 */
export function YouBlock({ event }: { event: ResearchEvent }) {
  const content = event.content || '';

  return (
    <div className="flex w-full flex-col gap-[6px] px-1 py-2 mt-[72px]">
      {/* Header: [YOU label] [Avatar] — right-aligned */}
      <div className="flex items-center justify-end gap-2">
        <span
          className="font-mono text-[11px] font-semibold uppercase tracking-wide"
          style={{ color: '#00FF00' }}
        >
          YOU
        </span>
        <span
          className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full"
          style={{ backgroundColor: '#00FF0015' }}
        >
          <User size={10} color="#00FF00" />
        </span>
      </div>

      {/* Message text — right-aligned */}
      <div className="whitespace-pre-wrap break-words text-right font-sans text-[13px] leading-[1.4] text-[#CCCCCC]">
        {content}
      </div>
    </div>
  );
}
