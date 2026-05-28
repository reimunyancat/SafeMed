"""Final risk score: Risk = α·Rule + β·PRR + γ·AE + δ·GCN.

Weights α > β > γ > δ per SafeMed spec. Each component is normalised to [0, 1]
before weighting, so the final raw score also lives in [0, 1] and maps to 0–100.

Band cutoffs (from spec):
    0–30  🟢 green
    31–60 🟡 yellow
    61–100 🔴 red
"""
from __future__ import annotations

from dataclasses import dataclass

from app.rules.dur import RuleFinding
from app.signal.gcn import GCNScore
from app.signal.prr import PRRResult

# Locked Phase 1 weights. Re-tune in Phase 6 against an eval set.
ALPHA_RULE = 0.45
BETA_PRR = 0.30
GAMMA_AE = 0.15
DELTA_GCN = 0.10

SEVERITY_WEIGHT = {"high": 1.0, "medium": 0.6, "low": 0.3}


@dataclass(frozen=True)
class RiskBreakdown:
    rule_component: float
    prr_component: float
    ae_component: float
    gcn_component: float
    raw_score: float
    score_0_100: int
    band: str  # "green" | "yellow" | "red"


def compute_risk(
    findings: list[RuleFinding],
    prr_results: list[PRRResult],
    ae_freq: float,
    gcn_scores: list[GCNScore],
) -> RiskBreakdown:
    # Rule component: sum of severities, clipped to 1.0 at ~3 high-severity hits.
    rule_raw = sum(SEVERITY_WEIGHT.get(f.severity, 0.3) for f in findings)
    rule_score = min(1.0, rule_raw / 3.0)

    # PRR component: average dampened PRR across signal-positive results.
    signal_results = [r for r in prr_results if r.is_signal]
    if prr_results:
        prr_score = min(
            1.0,
            sum(min(1.0, r.prr / 10.0) for r in signal_results) / max(1, len(prr_results)),
        )
    else:
        prr_score = 0.0

    ae_score = max(0.0, min(1.0, ae_freq))

    if gcn_scores:
        gcn_score = sum(s.risk_amplifier for s in gcn_scores) / len(gcn_scores)
    else:
        gcn_score = 0.0

    rule_c = ALPHA_RULE * rule_score
    prr_c = BETA_PRR * prr_score
    ae_c = GAMMA_AE * ae_score
    gcn_c = DELTA_GCN * gcn_score

    raw = rule_c + prr_c + ae_c + gcn_c
    score = int(round(raw * 100))
    if score <= 30:
        band = "green"
    elif score <= 60:
        band = "yellow"
    else:
        band = "red"
    return RiskBreakdown(
        rule_component=rule_c,
        prr_component=prr_c,
        ae_component=ae_c,
        gcn_component=gcn_c,
        raw_score=raw,
        score_0_100=score,
        band=band,
    )
