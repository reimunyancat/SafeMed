import type { CSSProperties } from "react";
import { TTSButton } from "./TTSButton";

interface Props {
  text: string;
}

const aiBadgeStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 4,
  padding: "2px 8px",
  borderRadius: 999,
  backgroundColor: "#fff1e8",
  color: "#f05d22",
  fontSize: 11,
  fontWeight: 600,
};

export function EasySummary({ text }: Props) {
  return (
    <div className="bg-white border border-brand-line rounded-2xl p-4 shadow-soft">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="text-sm font-semibold text-brand-ink">쉬운 요약</div>
          <span style={aiBadgeStyle} aria-label="AI가 생성한 요약">AI 요약</span>
        </div>
        <TTSButton text={text} label="들어보기" />
      </div>
      <p className="text-base text-brand-ink leading-relaxed whitespace-pre-wrap">
        {text}
      </p>
      <p className="text-[11px] text-brand-muted mt-2">
        AI가 생성한 요약이라 설명이 정확하지 않을 수 있어요.
      </p>
    </div>
  );
}
