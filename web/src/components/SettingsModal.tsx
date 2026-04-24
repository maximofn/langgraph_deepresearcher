import { FormEvent, useEffect, useRef, useState } from 'react';
import { X, ArrowUp, Sparkles } from 'lucide-react';
import { ApiKeysSection, ModelsSection, UserInfoSection } from './SettingsSections';
import { useSessionStore } from '@/state/sessionStore';

interface SettingsModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (input: {
    query: string;
    maxIterations: number;
    maxConcurrent: number;
  }) => Promise<void>;
}

function sliderGradient(value: number, min: number, max: number) {
  const pct = ((value - min) / (max - min)) * 100;
  return `linear-gradient(to right, #00FF00 ${pct}%, #1A1A1A ${pct}%)`;
}

export function SettingsModal({ open, onClose, onSubmit }: SettingsModalProps) {
  const [query, setQuery] = useState('');
  const [maxIterations, setMaxIterations] = useState(6);
  const [maxConcurrent, setMaxConcurrent] = useState(3);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedModels = useSessionStore((s) => s.selectedModels);
  const apiKeys = useSessionStore((s) => s.apiKeys);
  const modelsCatalog = useSessionStore((s) => s.modelsCatalog);
  const discoveredCatalog = useSessionStore((s) => s.discoveredCatalog);

  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
      return () => { document.body.style.overflow = ''; };
    }
  }, [open]);

  if (!open) return null;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim() || submitting) return;
    setError(null);

    const effectiveCatalog = discoveredCatalog ?? modelsCatalog;
    if (effectiveCatalog) {
      const filledEnvs = new Set(
        Object.entries(apiKeys).filter(([, v]) => v && v.trim().length > 0).map(([k]) => k),
      );
      const missingModels = effectiveCatalog.roles
        .map((role) => {
          const modelName = selectedModels[role];
          if (!modelName) return null;
          const model = effectiveCatalog.models.find((m) => m.name === modelName);
          if (model && !filledEnvs.has(model.api_key_env)) return model.label;
          return null;
        })
        .filter(Boolean) as string[];

      if (missingModels.length > 0) {
        const unique = [...new Set(missingModels)];
        setError(`API key missing for: ${unique.join(', ')}. Add your keys above before starting.`);
        return;
      }
    }

    setSubmitting(true);
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
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/80 p-4">
      <div
        className="my-8 flex w-[560px] max-h-[90vh] flex-col gap-6 rounded-2xl py-7 px-8 overflow-y-auto scrollbar-modal"
        style={{ background: '#111111', border: '1px solid #1A1A1A' }}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-white">New Research</h2>
          <button
            onClick={onClose}
            className="flex items-center justify-center transition-opacity hover:opacity-70"
            style={{ color: '#666666' }}
          >
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-6">
          <div className="flex flex-col gap-2">
            <label
              className="font-mono font-medium tracking-widest"
              style={{ fontSize: '11px', color: '#888888' }}
            >
              QUERY
            </label>
            <div
              className="flex items-start gap-3 px-4 py-3"
              style={{
                background: '#0A0A0A',
                border: '1px solid #222222',
                borderRadius: '10px',
              }}
            >
              <textarea
                ref={textareaRef}
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  const el = e.target;
                  el.style.height = 'auto';
                  el.style.height = `${el.scrollHeight}px`;
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (query.trim() && !submitting) handleSubmit(e as unknown as FormEvent);
                  }
                }}
                placeholder="What do you want to research?"
                className="new-research-input flex-1 bg-transparent outline-none resize-none overflow-hidden"
                style={{ fontSize: '14px', color: '#ffffff', minHeight: '24px', lineHeight: '24px' }}
                rows={1}
                autoFocus
              />
              <button
                type="submit"
                disabled={!query.trim() || submitting}
                className="flex flex-shrink-0 self-end items-center justify-center disabled:opacity-40"
                style={{
                  width: '32px',
                  height: '32px',
                  background: '#00FF00',
                  borderRadius: '8px',
                }}
              >
                <ArrowUp size={16} color="#0A0A0A" />
              </button>
            </div>
          </div>

          <div className="flex flex-col gap-5">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span style={{ fontSize: '13px', fontWeight: 500, color: '#CCCCCC' }}>
                  Max iterations
                </span>
                <span
                  className="font-mono"
                  style={{ fontSize: '13px', fontWeight: 600, color: '#00FF00' }}
                >
                  {maxIterations}
                </span>
              </div>
              <p style={{ fontSize: '12px', color: '#777777', lineHeight: 1.4 }}>
                Maximum number of supervisor cycles. Each cycle can delegate new
                research topics or refine previous ones. Higher values allow
                deeper exploration at the cost of more tokens and longer runs.
              </p>
              <input
                type="range"
                min={1}
                max={20}
                value={maxIterations}
                onChange={(e) => setMaxIterations(Number(e.target.value))}
                className="custom-slider w-full"
                style={{ background: sliderGradient(maxIterations, 1, 20) }}
              />
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span style={{ fontSize: '13px', fontWeight: 500, color: '#CCCCCC' }}>
                  Max concurrent researchers
                </span>
                <span
                  className="font-mono"
                  style={{ fontSize: '13px', fontWeight: 600, color: '#00FF00' }}
                >
                  {maxConcurrent}
                </span>
              </div>
              <p style={{ fontSize: '12px', color: '#777777', lineHeight: 1.4 }}>
                How many research sub-agents the supervisor can run in parallel.
                Higher values speed up broad topics but use more API quota and
                may hit rate limits.
              </p>
              <input
                type="range"
                min={1}
                max={10}
                value={maxConcurrent}
                onChange={(e) => setMaxConcurrent(Number(e.target.value))}
                className="custom-slider w-full"
                style={{ background: sliderGradient(maxConcurrent, 1, 10) }}
              />
            </div>
          </div>

          <UserInfoSection />
          <ApiKeysSection />
          <ModelsSection />

          {error && <div className="text-xs text-red-400">{error}</div>}

          <div className="flex flex-col gap-4">
            <hr style={{ borderColor: '#1A1A1A' }} />
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                className="rounded-[10px] px-5 py-2.5 text-sm font-medium transition-opacity hover:opacity-70"
                style={{ border: '1px solid #333333', color: '#AAAAAA' }}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!query.trim() || submitting}
                className="flex items-center gap-2 rounded-[10px] px-6 py-2.5 text-sm font-semibold disabled:opacity-40"
                style={{ background: '#00FF00', color: '#0A0A0A' }}
              >
                <Sparkles size={16} />
                {submitting ? 'Starting…' : 'Start Research'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
