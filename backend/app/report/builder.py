from __future__ import annotations

from app.rules.dur import RuleFinding
from app.schemas import FindingOut, RiskOut
from app.signal.risk import RiskBreakdown


def to_finding_outs(findings: list[RuleFinding]) -> list[FindingOut]:
    return [
        FindingOut(
            kind=f.kind,
            severity=f.severity,
            drug_a_name=f.drug_a_name,
            drug_b_name=f.drug_b_name,
            message=f.message,
            evidence=f.evidence,
        )
        for f in findings
    ]


def to_risk_out(rb: RiskBreakdown) -> RiskOut:
    return RiskOut(
        score=rb.score_0_100,
        band=rb.band,  # type: ignore[arg-type]
        rule_component=round(rb.rule_component, 4),
        prr_component=round(rb.prr_component, 4),
        ae_component=round(rb.ae_component, 4),
        gcn_component=round(rb.gcn_component, 4),
    )


def cautions_from_findings(findings: list[RuleFinding]) -> list[str]:
    cautions: list[str] = []
    seen: set[tuple[str, str]] = set()
    for f in findings:
        key = (f.kind, f.drug_a_name + (f.drug_b_name or ""))
        if key in seen:
            continue
        seen.add(key)
        if f.kind == "combo":
            cautions.append(f"{f.drug_a_name} + {f.drug_b_name}: 함께 드시면 안 돼요.")
        elif f.kind == "elderly":
            cautions.append(f"{f.drug_a_name}: 어르신께서는 주의가 필요해요.")
        elif f.kind == "pregnancy":
            cautions.append(f"{f.drug_a_name}: 임신 중에는 피하시는 게 좋아요.")
        elif f.kind == "age":
            cautions.append(
                f"{f.drug_a_name}: 특정 연령대(주로 소아·청소년)에는 사용이 제한돼요."
            )
        elif f.kind == "duplicate_class":
            cautions.append(f"{f.drug_a_name} + {f.drug_b_name}: 같은 계열이라 효과가 겹쳐요.")
        elif f.kind == "dosage":
            cautions.append(f"{f.drug_a_name}: 용량/투여기간 한도가 정해진 약이에요.")
    return cautions


def suggest_alternatives(findings: list[RuleFinding], band: str) -> list[str]:
    if not findings:
        return []

    kinds = {f.kind for f in findings}
    msgs: list[str] = []

    if band == "red":
        msgs.append("처방한 의사 또는 약사와 즉시 상의해 주세요.")
    elif band == "yellow":
        msgs.append("가까운 약국에 문의해 복용 가능 여부를 한 번 더 확인해 주세요.")

    if "combo" in kinds:
        msgs.append("병용금기 약물 중 하나를 다른 작용기전으로 바꿀 수 있는지 확인해 보세요.")
    if "duplicate_class" in kinds:
        msgs.append("같은 효능군 약물은 한 가지로 통일하는 게 안전한 경우가 많아요.")
    if "pregnancy" in kinds:
        msgs.append("임신·수유 중에는 안전 등급이 높은 대체제(예: 아세트아미노펜)가 우선 고려돼요.")
    if "elderly" in kinds:
        msgs.append("고령자에게는 항콜린성·진정 계열 약물 사용을 줄이는 게 권고됩니다.")
    if "age" in kinds:
        msgs.append("소아·청소년 금기 약물은 동일 효능군의 소아 허가 의약품으로 대체 가능한지 확인해 주세요.")
    if "dosage" in kinds:
        msgs.append("용량/투여기간 한도가 정해진 약은 자가 증량하지 말고 처방 그대로 복용해 주세요.")
    return msgs