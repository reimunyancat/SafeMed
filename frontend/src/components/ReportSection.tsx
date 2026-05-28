interface Props {
  detail: string;
  cautions: string[];
}

export function ReportSection({ detail, cautions }: Props) {
  return (
    <div className="flex flex-col gap-3">
      {detail && (
        <div className="bg-white border border-brand-line rounded-2xl p-4 shadow-soft">
          <div className="text-sm font-semibold text-brand-ink mb-2">자세한 설명</div>
          <p className="text-sm text-brand-ink leading-relaxed whitespace-pre-wrap">
            {detail}
          </p>
        </div>
      )}
      {cautions.length > 0 && (
        <div className="bg-white border border-brand-line rounded-2xl p-4 shadow-soft">
          <div className="text-sm font-semibold text-brand-ink mb-2">주의 사항</div>
          <ul className="flex flex-col gap-2">
            {cautions.map((c, i) => (
              <li
                key={i}
                className="text-sm text-brand-ink pl-3 border-l-2 border-medical-yellow"
              >
                {c}
              </li>
            ))}
          </ul>
        </div>
      )}
      <p className="text-xs text-brand-muted text-center px-2">
        이 점수는 참고용입니다. 의료적 진단·처방을 대체하지 않으며, 약 복용 전에 반드시 의사·약사 선생님과 상의하세요.
      </p>
    </div>
  );
}
