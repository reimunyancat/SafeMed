import type { CSSProperties } from "react";
import type { Band } from "../types";

interface Props {
  score: number;
  band: Band;
}

const BAND_COLOR: Record<Band, string> = {
  green: "#39b56a",
  yellow: "#f5bd26",
  red: "#ef4d3f",
};

const BAND_LABEL: Record<Band, string> = {
  green: "안전",
  yellow: "주의",
  red: "위험",
};

export function RiskGauge({ score, band }: Props) {
  const radius = 60;
  const stroke = 12;
  const circumference = 2 * Math.PI * radius;
  const progress = Math.max(0, Math.min(100, score));
  const dash = (progress / 100) * circumference;
  const color = BAND_COLOR[band];

  const transitionStyle: CSSProperties = { transition: "stroke-dasharray 0.6s ease" };
  const numberStyle: CSSProperties = { color };
  const badgeStyle: CSSProperties = { background: `${color}1a`, color };

  return (
    <div
      className="flex flex-col items-center"
      role="img"
      aria-label={`위험 점수 ${progress}점, ${BAND_LABEL[band]} 단계`}
    >
      <svg width={radius * 2 + stroke} height={radius * 2 + stroke}>
        <circle
          cx={radius + stroke / 2}
          cy={radius + stroke / 2}
          r={radius}
          stroke="#ececec"
          strokeWidth={stroke}
          fill="none"
        />
        <circle
          cx={radius + stroke / 2}
          cy={radius + stroke / 2}
          r={radius}
          stroke={color}
          strokeWidth={stroke}
          fill="none"
          strokeDasharray={`${dash} ${circumference}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${radius + stroke / 2} ${radius + stroke / 2})`}
          style={transitionStyle}
        />
      </svg>
      <div className="-mt-24 flex flex-col items-center">
        <div className="text-4xl font-bold" style={numberStyle}>
          {progress}
        </div>
        <div className="text-xs text-brand-muted">/ 100</div>
      </div>
      <div
        className="mt-6 px-3 py-1 rounded-full text-xs font-semibold"
        style={badgeStyle}
      >
        {BAND_LABEL[band]}
      </div>
    </div>
  );
}
