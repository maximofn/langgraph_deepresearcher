import type { SessionStatus } from '@/api/types';

const COLORS: Record<SessionStatus, string> = {
  created: 'bg-neutral-700 text-neutral-200',
  active: 'bg-sky-700 text-sky-100',
  clarification_needed: 'bg-amber-600 text-amber-100',
  completed: 'bg-emerald-700 text-emerald-100',
  failed: 'bg-red-700 text-red-100',
  expired: 'bg-neutral-800 text-neutral-400',
};

const LABELS: Record<SessionStatus, string> = {
  created: 'Created',
  active: 'Running',
  clarification_needed: 'Needs clarification',
  completed: 'Completed',
  failed: 'Failed',
  expired: 'Expired',
};

export function StatusBadge({ status }: { status: SessionStatus }) {
  return (
    <span
      className={`inline-block rounded px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${COLORS[status]}`}
    >
      {LABELS[status]}
    </span>
  );
}
