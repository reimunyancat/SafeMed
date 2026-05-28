import type { Finding, Severity } from "../types";

const SEV_LABEL: Record<Severity, string> = {
  high: "위험",
  medium: "주의",
  low: "참고",
};

const SEV_BG: Record<Severity, string> = {
  high: "bg-red-50 border-red-200 text-red-700",
  medium: "bg-yellow-50 border-yellow-200 text-yellow-700",
  low: "bg-blue-50 border-blue-200 text-blue-700",
};

interface Props {
  finding: Finding;
}

export function InteractionCard({ finding }: Props) {
  return (
    <div className="bg-white border border-brand-line rounded-2xl p-4 shadow-soft">
      <div className="flex items-center justify-between mb-2">
        <div className="text-sm font-semibold text-brand-ink">
          {finding.drug_a_name}
          {finding.drug_b_name && (
            <span className="text-brand-muted"> + {finding.drug_b_name}</span>
          )}
        </div>
        <span
          className={`text-xs px-2 py-0.5 rounded-full border ${SEV_BG[finding.severity]}`}
        >
          {SEV_LABEL[finding.severity]}
        </span>
      </div>
      <p className="text-sm text-brand-ink leading-relaxed">{finding.message}</p>
      {finding.evidence && (
        <p className="text-xs text-brand-muted mt-2">단서: {finding.evidence}</p>
      )}
    </div>
  );
}
