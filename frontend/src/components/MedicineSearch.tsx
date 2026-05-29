import { useEffect, useRef, useState } from "react";
import { searchMfds } from "../api/client";
import type { Drug, MfdsItem } from "../types";

interface Props {
  onAdd: (drug: Drug) => void;
  selected: Drug[];
}

function debounce<T extends (...args: any[]) => void>(fn: T, ms: number) {
  let t: ReturnType<typeof setTimeout> | null = null;
  return (...args: Parameters<T>) => {
    if (t) clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
}

export function MedicineSearch({ onAdd, selected }: Props) {
  const [query, setQuery] = useState("");
  const [items, setItems] = useState<MfdsItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const searchRef = useRef(
    debounce(async (q: string) => {
      if (!q.trim()) {
        setItems([]);
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const res = await searchMfds(q);
        setItems(res);
      } finally {
        setLoading(false);
      }
    }, 350),
  );

  useEffect(() => {
    setOpen(query.length > 0);
    searchRef.current(query);
  }, [query]);

  const isSelected = (seq: string) => selected.some((d) => d.item_seq === seq);

  return (
    <section className="px-5 pb-4">
      <label className="section-label">약 검색</label>
      <div className="relative">
        <input
          type="text"
          inputMode="search"
          placeholder="예시) 타이레놀, 아스피린"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setOpen(query.length > 0)}
          className="field-input pr-10"
          aria-label="약 이름 검색"
        />
        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-brand-muted">
          🔍
        </span>
        {open && (
          <div className="absolute z-20 mt-1 w-full bg-white rounded-xl border border-brand-line shadow-soft max-h-72 overflow-y-auto">
            {loading && (
              <div className="px-4 py-3 text-sm text-brand-muted">찾는 중…</div>
            )}
            {!loading && items.length === 0 && (
              <div className="px-4 py-3 text-sm text-brand-muted">
                결과가 없어요. 약 이름을 한글로 다시 입력해보세요.
              </div>
            )}
            {items.map((it) => {
              const already = isSelected(it.itemSeq);
              return (
                <button
                  key={it.itemSeq}
                  type="button"
                  disabled={already}
                  onClick={() => {
                    onAdd({
                      item_seq: it.itemSeq,
                      item_name: it.itemName,
                      entp_name: it.entpName,
                      efcy: it.efcyQesitm,
                      use_method: it.useMethodQesitm,
                      caution: it.atpnQesitm,
                      interaction: it.intrcQesitm,
                      ingredient_codes: it.ingredientCodes,
                    });
                    setQuery("");
                    setOpen(false);
                  }}
                  className={`w-full text-left px-4 py-3 border-b border-brand-line last:border-0 hover:bg-brand-surface ${
                    already ? "opacity-40 cursor-not-allowed" : ""
                  }`}
                >
                  <div className="text-sm font-semibold text-brand-ink">
                    {it.itemName}
                  </div>
                  {it.entpName && (
                    <div className="text-xs text-brand-muted mt-0.5">
                      {it.entpName}
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}
