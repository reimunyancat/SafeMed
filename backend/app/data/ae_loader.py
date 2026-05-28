"""KAERS 이상사례 보고 데이터 로더 + PRR/ROR 입력 변환.

# 원시자료 입수 경로
# KAERS 원시자료는 한국의약품안전관리원의 사전 협의·승인을 거쳐야 받을 수 있는
# 민감 데이터다. 자동 다운로드는 지원하지 않고, 받은 파일을 data/raw/ 아래에
# 다음 형식으로 두면 자동 인식한다:
#
#   kaers_drug_adr.csv
#     drug_code,adr_term,count
#
# drug_code 는 MFDS item_seq(품목일련번호) 또는 ATC 코드 어느 쪽이든 무방.
# 파일이 없으면 PRR/ROR/AE 컴포넌트는 0 이 되고, 위험점수는 룰·GCN 기반으로만
# 계산된다 (β + γ = 0.45 만큼 score 가 빠짐).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import structlog

from app.signal.prr import PRRResult, compute_prr

log = structlog.get_logger(__name__)

_AE_FILENAME = "kaers_drug_adr.csv"


def load_ae_reports(raw_dir: str | Path) -> pd.DataFrame:
    raw_dir = Path(raw_dir)
    p = raw_dir / _AE_FILENAME
    if not p.exists():
        return pd.DataFrame(columns=["drug_code", "adr_term", "count"])

    df: pd.DataFrame | None = None
    for enc in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            df = pd.read_csv(p, encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    if df is None:
        log.warning("kaers_decode_failed", path=str(p))
        return pd.DataFrame(columns=["drug_code", "adr_term", "count"])

    df.columns = [c.strip().lower() for c in df.columns]
    required = {"drug_code", "adr_term", "count"}
    if not required.issubset(df.columns):
        log.warning("kaers_columns_unexpected", got=list(df.columns))
        return pd.DataFrame(columns=["drug_code", "adr_term", "count"])

    df["count"] = pd.to_numeric(df["count"], errors="coerce").fillna(0).astype(int)
    df["drug_code"] = df["drug_code"].astype(str).str.strip()
    df["adr_term"] = df["adr_term"].astype(str).str.strip()
    return df[df["count"] > 0]


def build_prr_for_drugs(
    drug_codes: list[str], ae_df: pd.DataFrame
) -> list[PRRResult]:
    """약물별 최강 신호 1건만 반환.

    PRR 신호가 많이 나오는 약물은 자동으로 노이즈가 생기는데, UI 카드 단위
    표시에선 약물당 1건이 적당하다. (다중 신호는 향후 DataDashboard 단계)
    """
    if ae_df.empty or not drug_codes:
        return []

    grand_total = int(ae_df["count"].sum())
    drug_adr = ae_df.groupby(["drug_code", "adr_term"])["count"].sum()
    adr_total = ae_df.groupby("adr_term")["count"].sum()
    drug_total = ae_df.groupby("drug_code")["count"].sum()

    results: list[PRRResult] = []
    for code in drug_codes:
        if code not in drug_total.index:
            continue
        drug_n = int(drug_total[code])
        best: PRRResult | None = None
        for term, a_val in drug_adr.xs(code, level="drug_code").items():
            a = int(a_val)
            b = drug_n - a
            c = int(adr_total[term]) - a
            d = grand_total - a - b - c
            r = compute_prr(a, b, c, d)
            if r.is_signal and (best is None or r.prr > best.prr):
                best = r
        if best is not None:
            results.append(best)
    return results


def ae_frequency_score(drug_codes: list[str], ae_df: pd.DataFrame) -> float:
    """약물 보고빈도를 0~1 로 정규화.

    절대 보고 건수를 그대로 쓰면 인기 약물이 무조건 빨갛게 떠서 변별력이 0 이라,
    *전체 약물의 95 분위* 를 1.0 기준으로 잡고 분위 위치로 환산한다.
    """
    if ae_df.empty or not drug_codes:
        return 0.0
    drug_total = ae_df.groupby("drug_code")["count"].sum()
    if drug_total.empty:
        return 0.0
    p95 = float(drug_total.quantile(0.95)) or 1.0
    vals = [float(drug_total.get(c, 0)) / p95 for c in drug_codes]
    return min(1.0, max(0.0, sum(vals) / len(vals)))
