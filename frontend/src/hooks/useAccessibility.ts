import { useEffect, useState } from "react";

export interface A11yState {
  largeText: boolean;
}

const LS_LARGE = "safemed.a11y.largeText";

export function useAccessibility() {
  const [state, setState] = useState<A11yState>(() => ({
    largeText:
      typeof window !== "undefined" && localStorage.getItem(LS_LARGE) === "1",
  }));

  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle("large-text-mode", state.largeText);
    try {
      localStorage.setItem(LS_LARGE, state.largeText ? "1" : "0");
    } catch {
      /* ignore quota errors */
    }
  }, [state.largeText]);

  return {
    ...state,
    toggleLargeText: () => setState((s) => ({ ...s, largeText: !s.largeText })),
  };
}
