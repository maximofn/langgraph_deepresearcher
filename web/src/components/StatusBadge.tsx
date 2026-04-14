import type { SessionStatus } from '@/api/types';

const STYLES: Record<SessionStatus, { bg: string; color: string; label: string }> = {
  created: { bg: '#55555518', color: '#888888', label: 'Created' },
  active: { bg: '#FFB80018', color: '#FFB800', label: 'Running' },
  clarification_needed: { bg: '#FF6B0018', color: '#FF6B00', label: 'Clarify' },
  completed: { bg: '#00FF0018', color: '#00FF00', label: 'Completed' },
  failed: { bg: '#EF444418', color: '#EF4444', label: 'Failed' },
  expired: { bg: '#44444418', color: '#666666', label: 'Expired' },
};

export function StatusBadge({ status }: { status: SessionStatus }) {
  const s = STYLES[status];
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-[10px] px-2.5 py-1 font-mono text-[10px] font-medium"
      style={{ backgroundColor: s.bg, color: s.color }}
    >
      <span
        className="inline-block h-1.5 w-1.5 rounded-full"
        style={{ backgroundColor: s.color }}
      />
      {s.label}
    </span>
  );
}
