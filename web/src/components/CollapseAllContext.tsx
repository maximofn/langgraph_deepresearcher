import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';

interface CollapseAllState {
  // Incremented each time the user hits collapse-all or expand-all.
  // Blocks watch this via useEffect to sync their local collapsed state.
  version: number;
  target: boolean; // true = collapsed, false = expanded
  collapseAll: () => void;
  expandAll: () => void;
}

const CollapseAllContext = createContext<CollapseAllState | null>(null);

export function CollapseAllProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState({ version: 0, target: false });

  const value = useMemo<CollapseAllState>(
    () => ({
      version: state.version,
      target: state.target,
      collapseAll: () => setState((s) => ({ version: s.version + 1, target: true })),
      expandAll: () => setState((s) => ({ version: s.version + 1, target: false })),
    }),
    [state]
  );

  return <CollapseAllContext.Provider value={value}>{children}</CollapseAllContext.Provider>;
}

export function useCollapseAll() {
  return useContext(CollapseAllContext);
}
