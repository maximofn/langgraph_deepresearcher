import { Sparkles } from 'lucide-react';

interface HomePageProps {
  onNewResearch: () => void;
}

export function HomePage({ onNewResearch }: HomePageProps) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-6 p-10 text-center">
      <Sparkles size={42} className="text-emerald-400" />
      <div>
        <h1 className="text-2xl font-semibold">Deep Researcher</h1>
        <p className="mt-2 max-w-md text-sm text-neutral-400">
          Multi-agent research pipeline streaming live from the LangGraph supervisor.
          Create a new session or pick one from the sidebar.
        </p>
      </div>
      <button
        onClick={onNewResearch}
        className="rounded bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-600"
      >
        Start a new research
      </button>
    </div>
  );
}
