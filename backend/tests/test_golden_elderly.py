from __future__ import annotations

from app.rules import run_rules
from app.signal import compute_risk, score_drugs


def test_elderly_polypharmacy_finds_combo_and_elderly(dur_data_elderly_combo) -> None:
    item_seqs = ["WARFARIN-001", "ASPIRIN-001", "IBUPROFEN-001", "SIMVA-001", "OMEP-001"]
    item_names = {
        "WARFARIN-001": "와파린정",
        "ASPIRIN-001": "아스피린정",
        "IBUPROFEN-001": "이부프로펜정",
        "SIMVA-001": "심바스타틴정",
        "OMEP-001": "오메프라졸캡슐",
    }
    findings = run_rules(
        item_seqs,
        item_names,
        dur_data_elderly_combo,
        is_elderly=True,
        is_pregnant=False,
    )
    kinds = [f.kind for f in findings]
    assert kinds.count("combo") == 1
    assert kinds.count("elderly") == 2

    risk = compute_risk(
        findings,
        prr_results=[],
        ae_freq=0.0,
        gcn_scores=score_drugs(item_seqs),
    )

    assert risk.band in {"yellow", "red"}
    assert risk.score_0_100 >= 31