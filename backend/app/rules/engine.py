"""룰 엔진 오케스트레이터."""
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


def run_rules(
    item_seqs: list[str],
    item_names: dict[str, str],
    dur_data: dict[DurType, pd.DataFrame],
    *,
    is_elderly: bool = False,
    is_pregnant: bool = False,
) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    findings.extend(check_combo(item_seqs, item_names, dur_data["combo"]))
    findings.extend(
        check_elderly(item_seqs, item_names, dur_data["elderly"], is_elderly=is_elderly)
    )
    findings.extend(
        check_pregnancy(
            item_seqs, item_names, dur_data["pregnancy"], is_pregnant=is_pregnant
        )
    )
    findings.extend(
        check_duplicate_class(item_seqs, item_names, dur_data["duplicate_class"])
    )
    findings.extend(
        check_dosage_warning(
            item_seqs,
            item_names,
            dur_data.get("dosage", pd.DataFrame()),
            dur_data.get("period", pd.DataFrame()),
        )
    )
    return findings
