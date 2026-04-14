import { FormEvent, useState } from 'react';
import { X } from 'lucide-react';

interface SettingsModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (input: {
    query: string;
    maxIterations: number;
    maxConcurrent: number;
  }) => Promise<void>;
}

export function SettingsModal({ open, onClose, onSubmit }: SettingsModalProps) {
  const [query, setQuery] = useState('');
  const [maxIterations, setMaxIterations] = useState(6);
  const [maxConcurrent, setMaxConcurrent] = useState(3);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!open) return null;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim() || submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      await onSubmit({
        query: query.trim(),
        maxIterations,
        maxConcurrent,
      });
      setQuery('');
      onClose();
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to create session';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-lg rounded-lg border border-neutral-800 bg-neutral-900 shadow-2xl">
        <div className="flex items-center justify-between border-b border-neutral-800 px-5 py-3">
          <h2 className="text-sm font-semibold">New research</h2>
          <button onClick={onClose} className="text-neutral-500 hover:text-neutral-200">
            <X size={16} />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4 p-5">
          <div>
            <label className="mb-1 block text-xs font-medium text-neutral-400">
              Query
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="What do you want to research?"
              rows={3}
              className="w-full resize-none rounded bg-neutral-950 px-3 py-2 text-sm outline-none ring-1 ring-neutral-800 focus:ring-emerald-600"
              autoFocus
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-xs font-medium text-neutral-400">
                Max iterations ({maxIterations})
              </label>
              <input
                type="range"
                min={1}
                max={20}
                value={maxIterations}
                onChange={(e) => setMaxIterations(Number(e.target.value))}
                className="w-full"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-neutral-400">
                Max concurrent ({maxConcurrent})
              </label>
              <input
                type="range"
                min={1}
                max={10}
                value={maxConcurrent}
                onChange={(e) => setMaxConcurrent(Number(e.target.value))}
                className="w-full"
              />
            </div>
          </div>
          {error && <div className="text-xs text-red-400">{error}</div>}
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded px-3 py-1.5 text-sm text-neutral-400 hover:text-neutral-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!query.trim() || submitting}
              className="rounded bg-emerald-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-600 disabled:opacity-50"
            >
              {submitting ? 'Starting…' : 'Start research'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
