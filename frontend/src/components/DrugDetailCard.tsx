import type { Drug } from "../types";

interface Props {
  drug: Drug;
}

export function DrugDetailCard({ drug }: Props) {
  return (
    <div className="bg-white border border-brand-line rounded-2xl p-4 shadow-soft">
      <div className="text-sm font-semibold text-brand-ink">{drug.item_name}</div>
      {drug.entp_name && (
        <div className="text-xs text-brand-muted mt-0.5">{drug.entp_name}</div>
      )}
      <dl className="mt-3 flex flex-col gap-2 text-sm text-brand-ink">
        {drug.efcy && (
          <div>
            <dt className="text-xs text-brand-muted">효능</dt>
            <dd className="leading-relaxed">{drug.efcy}</dd>
          </div>
        )}
        {drug.use_method && (
          <div>
            <dt className="text-xs text-brand-muted">복용법</dt>
            <dd className="leading-relaxed">{drug.use_method}</dd>
          </div>
        )}
        {drug.caution && (
          <div>
            <dt className="text-xs text-brand-muted">주의사항</dt>
            <dd className="leading-relaxed">{drug.caution}</dd>
          </div>
        )}
      </dl>
    </div>
  );
}
