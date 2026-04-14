import { Download } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface FinalReportProps {
  markdown: string;
  filenameHint?: string;
}

export function FinalReport({ markdown, filenameHint = 'report' }: FinalReportProps) {
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
      <div className="mb-3 flex items-center justify-between">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-emerald-300">
          <span>📄</span> Final Report
        </h2>
        <button
          onClick={handleDownload}
          className="flex items-center gap-1 rounded bg-emerald-700 px-3 py-1 text-sm text-white hover:bg-emerald-600"
        >
          <Download size={14} /> Download .md
        </button>
      </div>
      <div className="markdown-body text-neutral-100">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
      </div>
    </div>
  );
}
