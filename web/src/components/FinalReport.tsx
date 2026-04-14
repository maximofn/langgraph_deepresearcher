import { useState } from 'react';
import { Download } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface FinalReportProps {
  markdown: string;
  filenameHint?: string;
}

export function FinalReport({ markdown, filenameHint = 'report' }: FinalReportProps) {
  const [collapsed, setCollapsed] = useState(false);

  const handleDownload = () => {
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filenameHint.replace(/[^a-zA-Z0-9_-]+/g, '_').slice(0, 40)}.md`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="my-4 rounded-lg border border-emerald-700 bg-emerald-950/30 p-5">
      <div className="mb-3 flex items-center justify-between gap-2">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-emerald-300">
          <span>📄</span> Final Report
        </h2>
        <div className="flex items-center gap-2">
          <button
            onClick={handleDownload}
            className="flex items-center gap-1 rounded bg-emerald-700 px-3 py-1 text-sm text-white hover:bg-emerald-600"
          >
            <Download size={14} /> Download .md
          </button>
          <button
            type="button"
            onClick={() => setCollapsed((c) => !c)}
            aria-label={collapsed ? 'Expand report' : 'Collapse report'}
            title={collapsed ? 'Expand' : 'Collapse'}
            className="rounded p-1 text-emerald-300 hover:bg-emerald-900/60 transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              className={`h-4 w-4 transition-transform ${collapsed ? '-rotate-90' : ''}`}
            >
              <path
                fillRule="evenodd"
                d="M5.23 7.21a.75.75 0 011.06.02L10 11.06l3.71-3.83a.75.75 0 111.08 1.04l-4.25 4.39a.75.75 0 01-1.08 0L5.21 8.27a.75.75 0 01.02-1.06z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>
      </div>
      {!collapsed && (
        <div className="markdown-body text-neutral-100">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}
