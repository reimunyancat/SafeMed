import { AccessibilityControls } from "./AccessibilityControls";
import type { A11yState } from "../hooks/useAccessibility";

interface Props {
  a11y: A11yState & {
    toggleLargeText: () => void;
  };
}

export function Header({ a11y }: Props) {
  return (
    <header className="flex items-center justify-between px-5 pt-6 pb-3">
      <div className="flex items-center gap-2">
        <div className="h-9 w-9 rounded-xl bg-brand-orange flex items-center justify-center text-white font-bold text-lg">
          S
        </div>
        <div>
          <div className="text-lg font-bold text-brand-ink leading-none">
            SafeMed
          </div>
          <div className="text-xs text-brand-muted mt-0.5">세이프메드</div>
        </div>
      </div>
      <AccessibilityControls
        largeText={a11y.largeText}
        onToggleLargeText={a11y.toggleLargeText}
      />
    </header>
  );
}
