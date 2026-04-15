import { useEffect, useId, useMemo, useState } from 'react';
import { ChevronDown, Download, FileText, Link as LinkIcon } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { useCollapseAll } from './CollapseAllContext';

interface FinalReportProps {
  markdown: string;
  filenameHint?: string;
}

function countSources(markdown: string): number {
  const urls = markdown.match(/https?:\/\/[^\s)\]]+/g);
  if (!urls) return 0;
  return new Set(urls).size;
}

export function FinalReport({ markdown, filenameHint = 'report' }: FinalReportProps) {
  const id = useId();
  const [collapsed, setCollapsed] = useState(false);
  const collapseAll = useCollapseAll();

  // Sync with global collapse/expand command
  useEffect(() => {
    if (!collapseAll || collapseAll.version === 0) return;
    setCollapsed(collapseAll.target);
  }, [collapseAll?.version, collapseAll?.target]);

  // Report this block's collapsed state back to the context
  const { registerBlock, unregisterBlock } = collapseAll ?? {};
  useEffect(() => {
    registerBlock?.(id, collapsed);
  }, [registerBlock, id, collapsed]);
  useEffect(() => {
    return () => unregisterBlock?.(id);
  }, [unregisterBlock, id]);

  const sourceCount = useMemo(() => countSources(markdown), [markdown]);

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
    <div
      className={`mt-2 pt-2 ${collapsed ? 'cursor-pointer' : ''}`}
      onClick={collapsed ? () => setCollapsed(false) : undefined}
      role={collapsed ? 'button' : undefined}
    >
      <div className="h-px w-full bg-[#1E1E1E]" />

      <div
        className={`flex items-center justify-between gap-4 pb-3 pt-4 ${
          collapsed ? '' : 'cursor-pointer'
        }`}
        onClick={!collapsed ? () => setCollapsed(true) : undefined}
      >
        <div className="flex items-center gap-2.5">
          <FileText size={18} className="text-white" />
          <span className="font-sans text-[16px] font-semibold text-white">
            Final Report
          </span>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setCollapsed((c) => !c);
            }}
            aria-label={collapsed ? 'Expand report' : 'Collapse report'}
            className="ml-1 text-[#444444] transition-colors hover:text-[#AAAAAA]"
          >
            <ChevronDown
              size={16}
              className={`transition-transform ${collapsed ? '-rotate-90' : ''}`}
            />
          </button>
        </div>
        <div className="flex items-center gap-2">
          {sourceCount > 0 && (
            <div className="flex items-center gap-1.5 rounded-[8px] border border-[#1E1E1E] px-3 py-1.5">
              <LinkIcon size={12} className="text-[#666666]" />
              <span className="font-mono text-[11px] text-[#666666]">
                {sourceCount} source{sourceCount === 1 ? '' : 's'}
              </span>
            </div>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleDownload();
            }}
            className="flex items-center gap-1.5 rounded-[8px] bg-[#00FF00] px-3.5 py-2 font-sans text-[12px] font-semibold text-black transition-[filter] hover:brightness-110"
          >
            <Download size={14} /> Download .md
          </button>
        </div>
      </div>

      {!collapsed && (
        <div className="rounded-[10px] border border-[#1E1E1E] bg-[#111111] px-7 pt-6 pb-7">
          <div className="markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}
