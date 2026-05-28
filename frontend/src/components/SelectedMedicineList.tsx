import type { Drug } from "../types";

interface Props {
  drugs: Drug[];
  onRemove: (item_seq: string) => void;
}

export function SelectedMedicineList({ drugs, onRemove }: Props) {
  if (drugs.length === 0) {
    return (
      <section className="px-5 pb-4">
        <div className="section-label">선택한 약</div>
        <div className="rounded-2xl border border-dashed border-brand-line px-4 py-6 text-sm text-brand-muted text-center">
          드시는 약을 검색해서 추가해주세요.
        </div>
      </section>
    );
  }
  return (
    <section className="px-5 pb-4">
      <div className="section-label">선택한 약 ({drugs.length})</div>
      <ul className="flex flex-col gap-2">
        {drugs.map((d) => (
          <li
            key={d.item_seq}
            className="flex items-center justify-between bg-white border border-brand-line rounded-xl px-4 py-3 shadow-soft"
          >
            <div className="min-w-0">
              <div className="text-sm font-semibold text-brand-ink truncate">
                {d.item_name}
              </div>
              {d.entp_name && (
                <div className="text-xs text-brand-muted truncate mt-0.5">
                  {d.entp_name}
                </div>
              )}
            </div>
            <button
              type="button"
              aria-label={`${d.item_name} 제거`}
              onClick={() => onRemove(d.item_seq)}
              className="ml-3 text-brand-muted hover:text-medical-red text-lg shrink-0"
            >
              ✕
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
