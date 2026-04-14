import { FormEvent, useState } from 'react';
import { Send } from 'lucide-react';

interface ClarifyInputProps {
  onSubmit: (clarification: string) => Promise<void>;
  disabled?: boolean;
}

export function ClarifyInput({ onSubmit, disabled }: ClarifyInputProps) {
  const [value, setValue] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!value.trim() || submitting) return;
    setSubmitting(true);
    try {
      await onSubmit(value.trim());
      setValue('');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="my-4 rounded-lg border border-amber-600 bg-amber-950/30 p-4"
    >
      <div className="mb-2 text-sm font-semibold text-amber-300">
        The agent needs more info to continue
      </div>
      <div className="flex gap-2">
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Type your clarification…"
          disabled={disabled || submitting}
          className="flex-1 rounded bg-neutral-900 px-3 py-2 text-sm outline-none ring-1 ring-neutral-700 focus:ring-amber-500"
        />
        <button
          type="submit"
          disabled={disabled || submitting || !value.trim()}
          className="flex items-center gap-1 rounded bg-amber-600 px-3 py-2 text-sm font-medium text-white hover:bg-amber-500 disabled:opacity-50"
        >
          <Send size={14} /> Send
        </button>
      </div>
    </form>
  );
}
