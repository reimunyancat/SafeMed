from __future__ import annotations

from app.rules import run_rules
from app.signal import compute_risk, score_drugs


def test_otc_safe_combination_is_green(dur_data_empty) -> None:
    item_seqs = ["VITC-001", "PROBI-001"]
    item_names = {"VITC-001": "비타민C정", "PROBI-001": "정장제캡슐"}
    findings = run_rules(
        item_seqs,
        item_names,
        dur_data_empty,
        is_elderly=False,
        is_pregnant=False,
    )
    assert findings == []

    risk = compute_risk(
        findings,
        prr_results=[],
        ae_freq=0.0,
        gcn_scores=score_drugs(item_seqs),
    )
    assert risk.band == "green"
    assert risk.score_0_100 <= 30