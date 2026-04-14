import { useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { BrainCircuit, Plus, Search, Settings, Trash2 } from 'lucide-react';

import { api } from '@/api/client';
import type { SessionStatus } from '@/api/types';
import { useSessionStore } from '@/state/sessionStore';
import { StatusBadge } from './StatusBadge';

const STATUS_FILTERS: Array<{ value: 'all' | SessionStatus; label: string }> = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Running' },
  { value: 'clarification_needed', label: 'Clarify' },
  { value: 'completed', label: 'Completed' },
];

const USER = { name: 'Maximo', email: 'maximo@example.com', initial: 'M' };

function formatRelative(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const s = Math.floor(diff / 1000);
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  if (d < 7) return `${d}d ago`;
  const w = Math.floor(d / 7);
  if (w < 5) return `${w}w ago`;
  return new Date(iso).toLocaleDateString();
}

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
    <aside className="flex h-full w-80 flex-col overflow-hidden bg-terminal-bg">
      {/* Brand + actions */}
      <div className="flex flex-col gap-4 px-4 pb-4 pt-6">
        <div className="flex items-center gap-3">
          <div
            className="flex h-7 w-7 items-center justify-center rounded-[8px] border border-[#00FF0040]"
            style={{
              background: 'linear-gradient(135deg, #00FF0030, #00FF0008)',
            }}
          >
            <BrainCircuit size={16} className="text-[#00FF00]" />
          </div>
          <span className="font-sans text-[15px] font-semibold text-white">
            Deep Researcher
          </span>
        </div>

        <button
          onClick={onNewResearch}
          className="flex h-10 w-full items-center justify-center gap-2 rounded-[8px] bg-[#00FF00] font-sans text-sm font-semibold text-black transition-[filter] hover:brightness-110"
        >
          <Plus size={16} strokeWidth={2.5} /> New Research
        </button>

        <div className="relative">
          <Search
            size={14}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[#666666]"
          />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search conversations..."
            className="h-9 w-full rounded-[8px] bg-terminal-surface pl-9 pr-3 font-sans text-[13px] text-terminal-textPrimary outline-none ring-1 ring-inset ring-[#1A1A1A] placeholder:text-[#666666] focus:ring-[#2A2A2A]"
          />
        </div>

        <div className="flex items-center gap-2">
          {STATUS_FILTERS.map((f) => {
            const active = statusFilter === f.value;
            return (
              <button
                key={f.value}
                onClick={() => setStatusFilter(f.value)}
                className={`rounded-[12px] px-3 py-1 font-mono text-[12px] transition-colors ${
                  active
                    ? 'bg-[#00FF0015] font-medium text-[#00FF00]'
                    : 'text-[#666666] hover:text-[#CCCCCC]'
                }`}
              >
                {f.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Conversation list */}
      <div className="scrollbar-thin flex flex-1 flex-col gap-1 overflow-y-auto p-2">
        {filtered.length === 0 && (
          <div className="p-6 text-center font-sans text-xs text-[#555555]">
            No sessions
          </div>
        )}
        {filtered.map((s) => {
          const active = activeId === s.id;
          return (
            <div
              key={s.id}
              onClick={() => navigate(`/session/${s.id}`)}
              className={`group relative cursor-pointer rounded-[8px] p-3 transition-colors ${
                active
                  ? 'border-l-[3px] border-[#00FF0040] bg-terminal-surface pl-[9px]'
                  : 'bg-[#0F0F0F] hover:bg-[#121212]'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div
                  className={`line-clamp-2 flex-1 font-sans text-[13px] font-medium leading-[1.3] ${
                    active ? 'text-white' : 'text-terminal-textPrimary'
                  }`}
                >
                  {s.initial_query}
                </div>
                <StatusBadge status={s.status} />
              </div>
              <div className="mt-1 flex items-center justify-between gap-2">
                <div className="line-clamp-1 flex-1 font-sans text-[11px] leading-[1.2] text-[#555555]">
                  {s.initial_query}
                </div>
                <span className="font-mono text-[10px] text-[#444444]">
                  {formatRelative(s.created_at)}
                </span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(s.id);
                }}
                className="absolute right-1 top-1 rounded p-1 text-[#555555] opacity-0 hover:bg-red-950/50 hover:text-red-300 group-hover:opacity-100"
                title="Delete"
              >
                <Trash2 size={12} />
              </button>
            </div>
          );
        })}
      </div>

      {/* User footer */}
      <div className="flex items-center gap-3 border-t border-[#1E1E1E] px-4 py-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#00FF0015]">
          <span className="font-sans text-sm font-semibold text-[#00FF00]">
            {USER.initial}
          </span>
        </div>
        <div className="min-w-0 flex-1">
          <div className="truncate font-sans text-[13px] font-medium text-[#DDDDDD]">
            {USER.name}
          </div>
          <div className="truncate font-mono text-[11px] text-[#444444]">
            {USER.email}
          </div>
        </div>
        <button
          className="rounded p-1 text-[#555555] hover:text-[#CCCCCC]"
          title="Settings"
        >
          <Settings size={18} />
        </button>
      </div>
    </aside>
  );
}
