"""Module 1-D: 용량주의 + 투여기간주의 (ingredient_code 매칭 지원)."""
from __future__ import annotations

import pandas as pd

from app.rules.dur import RuleFinding
from app.rules.types import DrugRef

def check_dosage_warning(
    drugs: list[DrugRef],
    dosage_df: pd.DataFrame,
    period_df: pd.DataFrame,
) -> list[RuleFinding]:
    findings: list[RuleFinding] = []

    by_seq = {d.item_seq: d for d in drugs if d.item_seq}
    by_code: dict[str, DrugRef] = {}
    for d in drugs:
        for code in d.ingredient_codes:
            by_code.setdefault(code, d)

    sources = (
        ("용량주의", dosage_df, "max_dose", "unit", "MFDS DUR 용량주의 목록"),
        ("투여기간주의", period_df, "max_days", None, "MFDS DUR 투여기간주의 목록"),
    )

    for label, df, limit_col, unit_col, fallback in sources:
        if df is None or df.empty:
            continue
        seen: set[str] = set()
        for _, row in df.iterrows():
            seq = row.get("item_seq", "")
            code = row.get("ingredient_code", "")
            matched: DrugRef | None = None
            if seq and seq in by_seq:
                matched = by_seq[seq]
            elif code and code in by_code:
                matched = by_code[code]
            if matched is None or matched.item_seq in seen:
                continue
            seen.add(matched.item_seq)
            limit = row.get(limit_col, "")
            unit = row.get(unit_col, "") if unit_col else ""
            limit_text = f" (한도 {limit}{unit})" if limit else ""
            findings.append(
                RuleFinding(
                    kind="dosage",
                    severity="low",
                    drug_a=matched.item_seq,
                    drug_a_name=matched.item_name,
                    drug_b=None,
                    drug_b_name=None,
                    message=f"{label}{limit_text} 대상 성분입니다.",
                    evidence=row.get("caution_content", "") or fallback,
                )
            )
    return findings
