import { useState } from "react";

interface Props {
  title: string;
  badge?: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}

export function PriorityDisclosure({ title, badge, defaultOpen = false, children }: Props) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="bg-white border border-brand-line rounded-2xl shadow-soft overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="w-full flex items-center justify-between px-4 py-3 text-left"
      >
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-brand-ink">{title}</span>
          {badge && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-brand-surface text-brand-muted">
              {badge}
            </span>
          )}
        </div>
        <span className={`text-brand-muted transition-transform ${open ? "rotate-180" : ""}`}>▾</span>
      </button>
      {open && <div className="px-4 pb-4">{children}</div>}
    </div>
  );
}
