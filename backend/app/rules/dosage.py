"""Module 1-D: 용량주의 + 투여기간주의.

# 1회/1일 복용량 정보는 아직 입력 채널이 없어서 (처방전 OCR 단계에서 들어옴),
# 현 단계에선 "해당 성분이 KIDS 용량/투여기간 주의 목록에 등재되어 있는가"
# 만 표시한다. 등재 여부 자체가 임상적 주의 신호다.
"""
from __future__ import annotations

import pandas as pd

from app.rules.dur import RuleFinding


def check_dosage_warning(
    item_seqs: list[str],
    item_names: dict[str, str],
    dosage_df: pd.DataFrame,
    period_df: pd.DataFrame,
) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    seq_set = set(item_seqs)

    sources = (
        ("용량주의", dosage_df, "max_dose", "unit", "MFDS DUR 용량주의 목록"),
        ("투여기간주의", period_df, "max_days", None, "MFDS DUR 투여기간주의 목록"),
    )

    for label, df, limit_col, unit_col, fallback_evidence in sources:
        if df is None or df.empty:
            continue
        for _, row in df.iterrows():
            seq = row.get("item_seq", "")
            if seq not in seq_set:
                continue
            limit = row.get(limit_col, "")
            unit = row.get(unit_col, "") if unit_col else ""
            limit_text = f" (한도 {limit}{unit})" if limit else ""
            findings.append(
                RuleFinding(
                    kind="dosage",
                    severity="low",
                    drug_a=seq,
                    drug_a_name=item_names.get(seq, row.get("item_name", "")),
                    drug_b=None,
                    drug_b_name=None,
                    message=f"{label}{limit_text} 대상 성분입니다.",
                    evidence=row.get("caution_content", "") or fallback_evidence,
                )
            )
    return findings
