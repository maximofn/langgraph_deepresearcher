import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';

interface CollapseAllState {
  version: number;
  target: boolean;
  /** True only when every registered block is collapsed. */
  allCollapsed: boolean;
  /** True only when every registered block is expanded. */
  allExpanded: boolean;
  collapseAll: () => void;
  expandAll: () => void;
  registerBlock: (id: string, collapsed: boolean) => void;
  unregisterBlock: (id: string) => void;
}

const CollapseAllContext = createContext<CollapseAllState | null>(null);

export function CollapseAllProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState({ version: 0, target: false });
  const [blockStates, setBlockStates] = useState<Map<string, boolean>>(new Map());

  const registerBlock = useCallback((id: string, collapsed: boolean) => {
    setBlockStates((prev) => {
      if (prev.get(id) === collapsed) return prev;
      const next = new Map(prev);
      next.set(id, collapsed);
      return next;
    });
  }, []);

  const unregisterBlock = useCallback((id: string) => {
    setBlockStates((prev) => {
      if (!prev.has(id)) return prev;
      const next = new Map(prev);
      next.delete(id);
      return next;
    });
  }, []);

  const value = useMemo<CollapseAllState>(() => {
    const blocks = [...blockStates.values()];
    const allCollapsed = blocks.length > 0 && blocks.every(Boolean);
    const allExpanded = blocks.length > 0 && blocks.every((c) => !c);
    return {
      version: state.version,
      target: state.target,
      allCollapsed,
      allExpanded,
      collapseAll: () => setState((s) => ({ version: s.version + 1, target: true })),
      expandAll: () => setState((s) => ({ version: s.version + 1, target: false })),
      registerBlock,
      unregisterBlock,
    };
  }, [state, blockStates, registerBlock, unregisterBlock]);

  return <CollapseAllContext.Provider value={value}>{children}</CollapseAllContext.Provider>;
}

export function useCollapseAll() {
  return useContext(CollapseAllContext);
}
