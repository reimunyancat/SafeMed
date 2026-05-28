import type { Profile } from "../types";

interface Props {
  value: Profile;
  onChange: (next: Profile) => void;
}

const CONDITIONS: { id: string; label: string }[] = [
  { id: "kidney", label: "신장질환" },
  { id: "liver", label: "간질환" },
  { id: "diabetes", label: "당뇨" },
  { id: "hypertension", label: "고혈압" },
  { id: "heart", label: "심장질환" },
];

export function ProfileForm({ value, onChange }: Props) {
  const toggleCond = (id: string) => {
    const has = value.conditions.includes(id);
    onChange({
      ...value,
      conditions: has
        ? value.conditions.filter((c) => c !== id)
        : [...value.conditions, id],
    });
  };

  return (
    <section className="px-5 pb-4">
      <div className="section-label">사용자 정보</div>
      <div className="flex flex-col gap-3 bg-white rounded-2xl border border-brand-line p-4 shadow-soft">
        <label className="flex items-center gap-3">
          <span className="w-16 text-sm text-brand-ink font-medium">나이</span>
          <input
            type="number"
            inputMode="numeric"
            min={0}
            max={120}
            value={value.age}
            onChange={(e) =>
              onChange({ ...value, age: Number(e.target.value) || 0 })
            }
            className="field-input w-24"
            aria-label="나이"
          />
          <span className="text-sm text-brand-muted">세</span>
        </label>

        <label className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={value.is_pregnant}
            onChange={(e) =>
              onChange({ ...value, is_pregnant: e.target.checked })
            }
            className="h-5 w-5 accent-brand-orange"
          />
          <span className="text-sm text-brand-ink">임신 중입니다</span>
        </label>

        <div>
          <div className="text-sm text-brand-ink font-medium mb-2">
            가지고 있는 질환
          </div>
          <div className="flex flex-wrap gap-2">
            {CONDITIONS.map((c) => {
              const active = value.conditions.includes(c.id);
              return (
                <button
                  type="button"
                  key={c.id}
                  aria-pressed={active}
                  onClick={() => toggleCond(c.id)}
                  className={`px-3 py-1.5 rounded-full text-xs border transition ${
                    active
                      ? "bg-brand-orange text-white border-brand-orange"
                      : "bg-white text-brand-ink border-brand-line"
                  }`}
                >
                  {c.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
