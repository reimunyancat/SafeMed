"""PRR + ROR + chi-squared signal mining.

References:
  - Evans SJW, Waller PC, Davis S. "Use of proportional reporting ratios (PRRs)
    for signal generation from spontaneous adverse drug reaction reports."
    Pharmacoepidemiol Drug Saf. 2001;10(6):483-486.
  - Rothman KJ, Lanes S, Sacks ST. "The reporting odds ratio and its advantages
    over the proportional reporting ratio." Pharmacoepidemiol Drug Saf. 2004;13:519-523.

EMA 신호 기준: PRR >= 2 AND chi-squared >= 4 AND a >= 3.
ROR 의 95% CI 하한이 1 초과면 보조 신호.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class PRRResult:
    a: int  # this drug, this ADR
    b: int  # this drug, other ADRs
    c: int  # other drugs, this ADR
    d: int  # other drugs, other ADRs
    prr: float
    chi2: float
    ror: float
    ror_ci_low: float
    ror_ci_high: float
    is_signal: bool


def compute_prr(a: int, b: int, c: int, d: int) -> PRRResult:
    if a + b == 0 or c + d == 0 or a + c == 0 or b + d == 0:
        return PRRResult(a, b, c, d, 0.0, 0.0, 0.0, 0.0, 0.0, False)

    p_drug = a / (a + b)
    p_other = c / (c + d)
    prr = p_drug / p_other if p_other > 0 else 0.0

    n = a + b + c + d
    num = n * (a * d - b * c) ** 2
    den = (a + b) * (c + d) * (a + c) * (b + d)
    chi2 = num / den if den > 0 else 0.0

    # ROR + 95% CI. 0-cell 은 Haldane-Anscombe 0.5 보정.
    aa = a if a > 0 else 0.5
    bb = b if b > 0 else 0.5
    cc = c if c > 0 else 0.5
    dd = d if d > 0 else 0.5
    ror = (aa * dd) / (bb * cc)
    se_lnror = math.sqrt(1 / aa + 1 / bb + 1 / cc + 1 / dd)
    ln_ror = math.log(ror) if ror > 0 else 0.0
    ci_low = math.exp(ln_ror - 1.96 * se_lnror)
    ci_high = math.exp(ln_ror + 1.96 * se_lnror)

    is_signal = prr >= 2.0 and chi2 >= 4.0 and a >= 3
    return PRRResult(a, b, c, d, prr, chi2, ror, ci_low, ci_high, is_signal)


def safe_log_prr(prr: float) -> float:
    if prr <= 0:
        return 0.0
    return max(0.0, math.log(prr))
