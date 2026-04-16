import { FormEvent, useState } from 'react';
import { MessageCircle, Send } from 'lucide-react';

interface PostResearchChatProps {
  onSubmit: (message: string) => Promise<void>;
  disabled?: boolean;
}

export function PostResearchChat({ onSubmit, disabled }: PostResearchChatProps) {
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
      style={{ borderLeftColor: '#4FC3F766', backgroundColor: '#0A0F15' }}
    >
      <div className="mb-2 flex items-center gap-2">
        <MessageCircle size={12} className="text-[#4FC3F7]" />
        <span className="font-mono text-[11px] font-semibold uppercase tracking-wide text-[#4FC3F7]">
          Ask me
        </span>
      </div>
      <div className="flex gap-2">
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Ask a follow-up question about the research…"
          disabled={disabled || submitting}
          className="h-9 flex-1 rounded-[8px] bg-terminal-surface px-3 font-sans text-[13px] text-terminal-textPrimary outline-none ring-1 ring-inset ring-[#1A1A1A] placeholder:text-[#666666] focus:ring-[#4FC3F766]"
        />
        <button
          type="submit"
          disabled={disabled || submitting || !value.trim()}
          className="flex items-center gap-1.5 rounded-[8px] bg-[#4FC3F7] px-4 font-sans text-[13px] font-semibold text-black transition-[filter] hover:brightness-110 disabled:opacity-50"
        >
          <Send size={14} /> Ask
        </button>
      </div>
    </form>
  );
}
