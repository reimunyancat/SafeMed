"""Therapeutic-class duplicate detection (ingredient_code 매칭 지원)."""
from __future__ import annotations

from collections import defaultdict

import pandas as pd

from app.rules.dur import RuleFinding
from app.rules.types import DrugRef

def check_duplicate_class(
    drugs: list[DrugRef],
    class_df: pd.DataFrame,
) -> list[RuleFinding]:
    if class_df.empty:
        return []

    by_seq = {d.item_seq: d for d in drugs if d.item_seq}
    by_code: dict[str, DrugRef] = {}
    for d in drugs:
        for code in d.ingredient_codes:
            by_code.setdefault(code, d)

    by_class: dict[str, list[DrugRef]] = defaultdict(list)
    class_name_map: dict[str, str] = {}

    for _, row in class_df.iterrows():
        cls = row.get("class_code", "")
        if not cls:
            continue
        if cls not in class_name_map:
            class_name_map[cls] = row.get("class_name", "")
        seq = row.get("item_seq", "")
        code = row.get("ingredient_code", "")
        matched: DrugRef | None = None
        if seq and seq in by_seq:
            matched = by_seq[seq]
        elif code and code in by_code:
            matched = by_code[code]
        if matched is None or matched in by_class[cls]:
            continue
        by_class[cls].append(matched)

    findings: list[RuleFinding] = []
    for cls, grouped in by_class.items():
        if len(grouped) < 2:
            continue
        class_name = class_name_map.get(cls, "")
        for i in range(len(grouped)):
            for j in range(i + 1, len(grouped)):
                a, b = grouped[i], grouped[j]
                findings.append(
                    RuleFinding(
                        kind="duplicate_class",
                        severity="medium",
                        drug_a=a.item_seq,
                        drug_a_name=a.item_name,
                        drug_b=b.item_seq,
                        drug_b_name=b.item_name,
                        message=f"같은 효능군({class_name or cls}) 약물 중복입니다.",
                        evidence="MFDS DUR 효능군 중복 목록",
                    )
                )
    return findings
