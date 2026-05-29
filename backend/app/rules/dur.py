"""DUR rule findings: combo / elderly / pregnancy.

item_seq 직접 매칭 + ingredient_code 매칭 둘 다 지원.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from app.rules.types import DrugRef

RuleKind = Literal["combo", "elderly", "pregnancy", "duplicate_class", "dosage"]
Severity = Literal["high", "medium", "low"]

@dataclass(frozen=True)
class RuleFinding:
    kind: RuleKind
    severity: Severity
    drug_a: str
    drug_a_name: str
    drug_b: str | None
    drug_b_name: str | None
    message: str
    evidence: str

def _build_lookups(
    drugs: list[DrugRef],
) -> tuple[dict[str, DrugRef], dict[str, DrugRef]]:
    by_seq = {d.item_seq: d for d in drugs if d.item_seq}
    by_code: dict[str, DrugRef] = {}
    for d in drugs:
        for code in d.ingredient_codes:
            by_code.setdefault(code, d)
    return by_seq, by_code

def _match(
    row,
    by_seq: dict[str, DrugRef],
    by_code: dict[str, DrugRef],
    seq_col: str = "item_seq",
    code_col: str = "ingredient_code",
) -> DrugRef | None:
    seq = row.get(seq_col, "")
    if seq and seq in by_seq:
        return by_seq[seq]
    code = row.get(code_col, "")
    if code and code in by_code:
        return by_code[code]
    return None

def check_combo(
    drugs: list[DrugRef],
    combo_df: pd.DataFrame,
) -> list[RuleFinding]:
    if combo_df.empty:
        return []
    by_seq, by_code = _build_lookups(drugs)
    findings: list[RuleFinding] = []
    seen: set[tuple[str, str]] = set()
    for _, row in combo_df.iterrows():
        a = _match(row, by_seq, by_code, seq_col="item_seq_a", code_col="ingredient_code_a")
        b = _match(row, by_seq, by_code, seq_col="item_seq_b", code_col="ingredient_code_b")
        if a is None or b is None or a.item_seq == b.item_seq:
            continue
        key = tuple(sorted([a.item_seq, b.item_seq]))
        if key in seen:
            continue
        seen.add(key)
        findings.append(
            RuleFinding(
                kind="combo",
                severity="high",
                drug_a=a.item_seq,
                drug_a_name=a.item_name,
                drug_b=b.item_seq,
                drug_b_name=b.item_name,
                message="병용금기 약물 조합입니다.",
                evidence=row.get("prohibit_content", "") or "MFDS DUR 병용금기 목록",
            )
        )
    return findings

def check_elderly(
    drugs: list[DrugRef],
    elderly_df: pd.DataFrame,
    *,
    is_elderly: bool,
) -> list[RuleFinding]:
    if not is_elderly or elderly_df.empty:
        return []
    by_seq, by_code = _build_lookups(drugs)
    findings: list[RuleFinding] = []
    seen: set[str] = set()
    for _, row in elderly_df.iterrows():
        matched = _match(row, by_seq, by_code)
        if matched is None or matched.item_seq in seen:
            continue
        seen.add(matched.item_seq)
        findings.append(
            RuleFinding(
                kind="elderly",
                severity="medium",
                drug_a=matched.item_seq,
                drug_a_name=matched.item_name,
                drug_b=None,
                drug_b_name=None,
                message="고령자에게 주의가 필요한 약물입니다.",
                evidence=row.get("caution_content", "") or "MFDS DUR 노인주의 목록",
            )
        )
    return findings

def check_pregnancy(
    drugs: list[DrugRef],
    preg_df: pd.DataFrame,
    *,
    is_pregnant: bool,
) -> list[RuleFinding]:
    if not is_pregnant or preg_df.empty:
        return []
    by_seq, by_code = _build_lookups(drugs)
    findings: list[RuleFinding] = []
    seen: set[tuple[str, str]] = set()
    for _, row in preg_df.iterrows():
        matched = _match(row, by_seq, by_code)
        if matched is None:
            continue
        grade = row.get("grade", "")
        key = (matched.item_seq, grade)
        if key in seen:
            continue
        seen.add(key)
        sev: Severity = "high" if grade in {"X", "D"} else "medium"
        findings.append(
            RuleFinding(
                kind="pregnancy",
                severity=sev,
                drug_a=matched.item_seq,
                drug_a_name=matched.item_name,
                drug_b=None,
                drug_b_name=None,
                message=f"임부금기 등급 {grade or '미상'} 약물입니다.",
                evidence=row.get("caution_content", "") or "MFDS DUR 임부금기 목록",
            )
        )
    return findings
