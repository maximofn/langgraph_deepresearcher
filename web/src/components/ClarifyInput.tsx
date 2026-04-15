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
      className="my-3 rounded-[8px] border-l-[3px] px-4 py-3"
      style={{ borderLeftColor: '#FF6B6B66', backgroundColor: '#150A0A' }}
    >
      <div className="mb-2 flex items-center gap-2">
        <span className="inline-block h-2 w-2 rounded-full bg-[#FF6B6B]" />
        <span className="font-mono text-[11px] font-semibold uppercase tracking-wide text-[#FF6B6B]">
          Awaiting clarification
        </span>
      </div>
      <div className="flex gap-2">
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Type your clarification…"
          disabled={disabled || submitting}
          className="h-9 flex-1 rounded-[8px] bg-terminal-surface px-3 font-sans text-[13px] text-terminal-textPrimary outline-none ring-1 ring-inset ring-[#1A1A1A] placeholder:text-[#666666] focus:ring-[#FF6B6B66]"
        />
        <button
          type="submit"
          disabled={disabled || submitting || !value.trim()}
          className="flex items-center gap-1.5 rounded-[8px] bg-[#FF6B6B] px-4 font-sans text-[13px] font-semibold text-black transition-[filter] hover:brightness-110 disabled:opacity-50"
        >
          <Send size={14} /> Send
        </button>
      </div>
    </form>
  );
}
