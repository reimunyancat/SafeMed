import type { RiskOut } from "../types";

interface Props {
  risk: RiskOut;
}

const LABELS: { key: keyof RiskOut; label: string; weight: string }[] = [
  { key: "rule_component", label: "규칙 검사", weight: "45%" },
  { key: "prr_component", label: "신호 탐지 (PRR)", weight: "30%" },
  { key: "ae_component", label: "부작용 빈도", weight: "15%" },
  { key: "gcn_component", label: "관계 네트워크", weight: "10%" },
];

export function RiskBreakdown({ risk }: Props) {
  const maxByWeight: Record<string, number> = {
    rule_component: 0.45,
    prr_component: 0.3,
    ae_component: 0.15,
    gcn_component: 0.1,
  };
  return (
    <div className="px-5 pb-4">
      <div className="section-label">점수 구성</div>
      <div className="flex flex-col gap-2 bg-white border border-brand-line rounded-2xl p-4 shadow-soft">
        {LABELS.map(({ key, label, weight }) => {
          const v = Number(risk[key]) || 0;
          const max = maxByWeight[key];
          const pct = Math.max(0, Math.min(100, (v / max) * 100));
          return (
            <div key={key}>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-brand-ink">
                  {label} <span className="text-brand-muted">({weight})</span>
                </span>
                <span className="text-brand-muted">{v.toFixed(2)}</span>
              </div>
              <div className="h-2 rounded-full bg-brand-surface overflow-hidden">
                <div
                  className="h-full bg-brand-orange transition-all duration-500"
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
