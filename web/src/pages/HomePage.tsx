import { Sparkles } from 'lucide-react';

interface HomePageProps {
  onNewResearch: () => void;
}

export function HomePage({ onNewResearch }: HomePageProps) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-6 p-10 text-center">
      <Sparkles size={42} className="text-[#00FF00]" />
      <div>
        <h1 className="text-2xl font-semibold text-terminal-text">Deep Researcher</h1>
        <p className="mt-2 max-w-md text-sm text-terminal-muted">
          Multi-agent research pipeline streaming live from the LangGraph supervisor.
          Create a new session or pick one from the sidebar.
        </p>
      </div>
      <button
        onClick={onNewResearch}
        className="rounded-[8px] bg-[#00FF00] px-4 py-2 font-sans text-sm font-semibold text-black transition-[filter] hover:brightness-110"
      >
        Start a new research
      </button>
    </div>
  );
}
