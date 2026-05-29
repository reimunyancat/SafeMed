"""룰 엔진 오케스트레이터 (DrugRef 기반)."""
from __future__ import annotations

import pandas as pd

from app.data.csv_loader import DurType
from app.rules.dosage import check_dosage_warning
from app.rules.dur import (
    RuleFinding,
    check_combo,
    check_elderly,
    check_pregnancy,
)
from app.rules.duplicate import check_duplicate_class
from app.rules.types import DrugRef

def run_rules(
    drugs: list[DrugRef],
    dur_data: dict[DurType, pd.DataFrame],
    *,
    is_elderly: bool = False,
    is_pregnant: bool = False,
) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    findings.extend(check_combo(drugs, dur_data["combo"]))
    findings.extend(check_elderly(drugs, dur_data["elderly"], is_elderly=is_elderly))
    findings.extend(check_pregnancy(drugs, dur_data["pregnancy"], is_pregnant=is_pregnant))
    findings.extend(check_duplicate_class(drugs, dur_data["duplicate_class"]))
    findings.extend(
        check_dosage_warning(
            drugs,
            dur_data.get("dosage", pd.DataFrame()),
            dur_data.get("period", pd.DataFrame()),
        )
    )
    return findings
