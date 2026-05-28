import { useEffect, useState } from "react";

export interface A11yState {
  largeText: boolean;
  highContrast: boolean;
}

const LS_LARGE = "safemed.a11y.largeText";
const LS_CONTRAST = "safemed.a11y.highContrast";

export function useAccessibility() {
  const [state, setState] = useState<A11yState>(() => ({
    largeText:
      typeof window !== "undefined" && localStorage.getItem(LS_LARGE) === "1",
    highContrast:
      typeof window !== "undefined" && localStorage.getItem(LS_CONTRAST) === "1",
  }));

  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle("large-text-mode", state.largeText);
    root.classList.toggle("high-contrast-mode", state.highContrast);
    try {
      localStorage.setItem(LS_LARGE, state.largeText ? "1" : "0");
      localStorage.setItem(LS_CONTRAST, state.highContrast ? "1" : "0");
    } catch {
      /* ignore quota errors */
    }
  }, [state.largeText, state.highContrast]);

  return {
    ...state,
    toggleLargeText: () =>
      setState((s) => ({ ...s, largeText: !s.largeText })),
    toggleHighContrast: () =>
      setState((s) => ({ ...s, highContrast: !s.highContrast })),
  };
}
