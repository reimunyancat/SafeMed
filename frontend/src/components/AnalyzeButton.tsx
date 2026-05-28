interface Props {
  disabled: boolean;
  loading: boolean;
  onClick: () => void;
}

export function AnalyzeButton({ disabled, loading, onClick }: Props) {
  return (
    <div className="px-5 pb-4">
      <button
        type="button"
        disabled={disabled || loading}
        onClick={onClick}
        className={`w-full rounded-2xl py-4 text-base font-bold transition shadow-soft ${
          disabled || loading
            ? "bg-brand-line text-brand-muted cursor-not-allowed"
            : "bg-brand-orange hover:bg-brand-orangeDark text-white"
        }`}
      >
        {loading ? "분석하는 중…" : "안전하게 확인하기"}
      </button>
    </div>
  );
}
