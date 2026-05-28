"""DUR 룰 결과 타입 + 1-A / 1-B / 1-C 체크.

# RuleKind 에 "dosage" 가 포함되어 있다. Module 1-D 의 용량/투여기간 주의도
# 동일한 finding 컨테이너를 쓰지만, 실제 검사는 rules/dosage.py 가 담당한다.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

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


def check_combo(
    item_seqs: list[str],
    item_names: dict[str, str],
    combo_df: pd.DataFrame,
) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    seq_set = set(item_seqs)
    if combo_df.empty:
        return findings
    for _, row in combo_df.iterrows():
        a = row.get("item_seq_a", "")
        b = row.get("item_seq_b", "")
        if a in seq_set and b in seq_set:
            findings.append(
                RuleFinding(
                    kind="combo",
                    severity="high",
                    drug_a=a,
                    drug_a_name=item_names.get(a, row.get("item_name_a", "")),
                    drug_b=b,
                    drug_b_name=item_names.get(b, row.get("item_name_b", "")),
                    message="병용금기 약물 조합입니다.",
                    evidence=row.get("prohibit_content", "") or "MFDS DUR 병용금기 목록",
                )
            )
    return findings


def check_elderly(
    item_seqs: list[str],
    item_names: dict[str, str],
    elderly_df: pd.DataFrame,
    *,
    is_elderly: bool,
) -> list[RuleFinding]:
    if not is_elderly or elderly_df.empty:
        return []
    findings: list[RuleFinding] = []
    seq_set = set(item_seqs)
    for _, row in elderly_df.iterrows():
        seq = row.get("item_seq", "")
        if seq in seq_set:
            findings.append(
                RuleFinding(
                    kind="elderly",
                    severity="medium",
                    drug_a=seq,
                    drug_a_name=item_names.get(seq, row.get("item_name", "")),
                    drug_b=None,
                    drug_b_name=None,
                    message="고령자에게 주의가 필요한 약물입니다.",
                    evidence=row.get("caution_content", "") or "MFDS DUR 노인주의 목록",
                )
            )
    return findings


def check_pregnancy(
    item_seqs: list[str],
    item_names: dict[str, str],
    preg_df: pd.DataFrame,
    *,
    is_pregnant: bool,
) -> list[RuleFinding]:
    if not is_pregnant or preg_df.empty:
        return []
    findings: list[RuleFinding] = []
    seq_set = set(item_seqs)
    for _, row in preg_df.iterrows():
        seq = row.get("item_seq", "")
        if seq in seq_set:
            grade = row.get("grade", "")
            # X, D 등급은 태아 위해 가능성 매우 높음 → high
            sev: Severity = "high" if grade in {"X", "D"} else "medium"
            findings.append(
                RuleFinding(
                    kind="pregnancy",
                    severity=sev,
                    drug_a=seq,
                    drug_a_name=item_names.get(seq, row.get("item_name", "")),
                    drug_b=None,
                    drug_b_name=None,
                    message=f"임부금기 등급 {grade or '미상'} 약물입니다.",
                    evidence=row.get("caution_content", "") or "MFDS DUR 임부금기 목록",
                )
            )
    return findings
