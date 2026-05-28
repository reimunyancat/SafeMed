import type { AnalyzeResponse, Drug } from "../types";
import { DrugDetailCard } from "./DrugDetailCard";
import { EasySummary } from "./EasySummary";
import { InteractionCard } from "./InteractionCard";
import { PriorityDisclosure } from "./PriorityDisclosure";
import { ReportSection } from "./ReportSection";
import { RiskBreakdown } from "./RiskBreakdown";
import { RiskGauge } from "./RiskGauge";

interface Props {
  result: AnalyzeResponse;
  drugs: Drug[];
}

export function ResultDashboard({ result, drugs }: Props) {
  const high = result.findings.filter((f) => f.severity === "high");
  const medium = result.findings.filter((f) => f.severity === "medium");
  const low = result.findings.filter((f) => f.severity === "low");

  return (
    <div className="flex flex-col gap-4 px-5 pb-8">
      <div className="bg-white border border-brand-line rounded-2xl p-5 shadow-soft flex flex-col items-center">
        <RiskGauge score={result.risk.score} band={result.risk.band} />
      </div>

      <EasySummary text={result.easy_summary} />

      {high.length > 0 && (
        <PriorityDisclosure
          title="⚠️ 당장 확인이 필요해요"
          badge={`${high.length}건`}
          defaultOpen
        >
          <div className="flex flex-col gap-2 mt-2">
            {high.map((f, i) => (
              <InteractionCard key={i} finding={f} />
            ))}
          </div>
        </PriorityDisclosure>
      )}

      {medium.length > 0 && (
        <PriorityDisclosure title="주의하면 좋아요" badge={`${medium.length}건`}>
          <div className="flex flex-col gap-2 mt-2">
            {medium.map((f, i) => (
              <InteractionCard key={i} finding={f} />
            ))}
          </div>
        </PriorityDisclosure>
      )}

      {low.length > 0 && (
        <PriorityDisclosure title="참고 사항" badge={`${low.length}건`}>
          <div className="flex flex-col gap-2 mt-2">
            {low.map((f, i) => (
              <InteractionCard key={i} finding={f} />
            ))}
          </div>
        </PriorityDisclosure>
      )}

      {result.findings.length === 0 && (
        <div className="bg-white border border-brand-line rounded-2xl p-4 shadow-soft text-sm text-brand-ink leading-relaxed">
          입력하신 약 조합에서 특별한 위험 조합은 않아요.
          그래도 새 약을 드실 때는 항상 약사 선생님께 알려주세요.
        </div>
      )}

      <ReportSection detail={result.detail_summary} cautions={result.cautions} />

      <RiskBreakdown risk={result.risk} />

      <PriorityDisclosure title="설정하신 약 상세 정보" badge={`${drugs.length}개`}>
        <div className="flex flex-col gap-2 mt-2">
          {drugs.map((d) => (
            <DrugDetailCard key={d.item_seq} drug={d} />
          ))}
        </div>
      </PriorityDisclosure>
    </div>
  );
}
