import { useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Plus, Search, Trash2 } from 'lucide-react';

import { api } from '@/api/client';
import type { SessionStatus } from '@/api/types';
import { useSessionStore } from '@/state/sessionStore';
import { StatusBadge } from './StatusBadge';

const STATUS_FILTERS: Array<{ value: 'all' | SessionStatus; label: string }> = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Running' },
  { value: 'clarification_needed', label: 'Needs clarify' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
];

interface SidebarProps {
  onNewResearch: () => void;
}

export function Sidebar({ onNewResearch }: SidebarProps) {
  const sessions = useSessionStore((s) => s.sessions);
  const removeSession = useSessionStore((s) => s.removeSession);
  const { id: activeId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | SessionStatus>('all');

  const filtered = useMemo(() => {
    return sessions.filter((s) => {
      if (statusFilter !== 'all' && s.status !== statusFilter) return false;
      if (search && !s.initial_query.toLowerCase().includes(search.toLowerCase())) return false;
      return true;
    });
  }, [sessions, search, statusFilter]);

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this session and all its events?')) return;
    try {
      await api.deleteSession(id);
      removeSession(id);
      if (activeId === id) navigate('/');
    } catch (err) {
      console.error('delete failed', err);
      alert('Failed to delete session');
    }
  };

  return (
    <aside className="flex h-full w-80 flex-col border-r border-neutral-800 bg-neutral-950">
      <div className="border-b border-neutral-800 p-4">
        <button
          onClick={onNewResearch}
          className="flex w-full items-center justify-center gap-2 rounded bg-emerald-700 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-600"
        >
          <Plus size={14} /> New research
        </button>
      </div>

      <div className="border-b border-neutral-800 p-3">
        <div className="relative mb-2">
          <Search
            size={14}
            className="absolute left-2 top-1/2 -translate-y-1/2 text-neutral-500"
          />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search…"
            className="w-full rounded bg-neutral-900 py-1.5 pl-7 pr-2 text-sm outline-none ring-1 ring-neutral-800 focus:ring-neutral-600"
          />
        </div>
        <div className="flex flex-wrap gap-1">
          {STATUS_FILTERS.map((f) => (
            <button
              key={f.value}
              onClick={() => setStatusFilter(f.value)}
              className={`rounded px-2 py-0.5 text-[10px] uppercase tracking-wide ${
                statusFilter === f.value
                  ? 'bg-neutral-200 text-neutral-900'
                  : 'bg-neutral-800 text-neutral-400 hover:text-neutral-200'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      <div className="scrollbar-thin flex-1 overflow-y-auto">
        {filtered.length === 0 && (
          <div className="p-6 text-center text-xs text-neutral-500">No sessions</div>
        )}
        {filtered.map((s) => (
          <div
            key={s.id}
            onClick={() => navigate(`/session/${s.id}`)}
            className={`group cursor-pointer border-b border-neutral-900 px-3 py-3 hover:bg-neutral-900 ${
              activeId === s.id ? 'bg-neutral-900' : ''
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0 flex-1">
                <div className="line-clamp-2 text-sm text-neutral-100">
                  {s.initial_query}
                </div>
                <div className="mt-1 flex items-center gap-2">
                  <StatusBadge status={s.status} />
                  <span className="text-[10px] text-neutral-500">
                    {new Date(s.created_at).toLocaleString()}
                  </span>
                </div>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(s.id);
                }}
                className="rounded p-1 text-neutral-500 opacity-0 hover:bg-red-950 hover:text-red-300 group-hover:opacity-100"
                title="Delete"
              >
                <Trash2 size={14} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}
