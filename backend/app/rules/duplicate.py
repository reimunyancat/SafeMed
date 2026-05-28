"""Therapeutic-class duplicate detection."""
from __future__ import annotations

from collections import defaultdict

import pandas as pd

from app.rules.dur import RuleFinding


def check_duplicate_class(
    item_seqs: list[str],
    item_names: dict[str, str],
    class_df: pd.DataFrame,
) -> list[RuleFinding]:
    if class_df.empty:
        return []
    seq_set = set(item_seqs)
    by_class: dict[str, list[tuple[str, str]]] = defaultdict(list)

    class_name_map: dict[str, str] = {}
    for _, row in class_df.iterrows():
        seq = row.get("item_seq", "")
        cls = row.get("class_code", "")
        if cls and cls not in class_name_map:
            class_name_map[cls] = row.get("class_name", "")
        if seq not in seq_set or not cls:
            continue
        by_class[cls].append((seq, item_names.get(seq, row.get("item_name", ""))))

    findings: list[RuleFinding] = []
    for cls, drugs in by_class.items():
        if len(drugs) < 2:
            continue
        for i in range(len(drugs)):
            for j in range(i + 1, len(drugs)):
                a_seq, a_name = drugs[i]
                b_seq, b_name = drugs[j]
                class_name = class_name_map.get(cls, "")
                findings.append(
                    RuleFinding(
                        kind="duplicate_class",
                        severity="medium",
                        drug_a=a_seq,
                        drug_a_name=a_name,
                        drug_b=b_seq,
                        drug_b_name=b_name,
                        message=f"같은 효능군({class_name or cls}) 약물 중복입니다.",
                        evidence="MFDS DUR 효능군 중복 목록",
                    )
                )
    return findings
