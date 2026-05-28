from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import Settings, get_settings
from app.core.errors import LLMUnavailableError
from app.data.ae_loader import (
    ae_frequency_score,
    build_prr_for_drugs,
    load_ae_reports,
)
from app.data.csv_loader import has_any_real_data, load_all
from app.report import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    call_llm,
    cautions_from_findings,
    fallback_template,
    parse_two_paragraphs,
    render_drug_list,
    render_findings,
    suggest_alternatives,
    to_finding_outs,
    to_risk_out,
)
from app.rules import run_rules
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.signal import compute_risk, score_drugs

router = APIRouter()

# data/raw 에서만 읽음 — sample 폴백은 제거했다.
_PROJECT_DATA = Path(__file__).resolve().parents[2].parent / "data"
_RAW_DIR = _PROJECT_DATA / "raw"


def _get_dur_data() -> dict:
    data = load_all(_RAW_DIR)
    if not has_any_real_data(data):
        raise HTTPException(
            status_code=422,
            detail=(
                "data/raw/ 에 DUR CSV 가 없어요. "
                "`uv --project backend run python scripts/fetch_dur_csv.py` 를 먼저 실행해주세요."
            ),
        )
    return data


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    req: AnalyzeRequest,
    settings: Settings = Depends(get_settings),
) -> AnalyzeResponse:
    item_seqs = [d.item_seq for d in req.drugs]
    item_names = {d.item_seq: d.item_name for d in req.drugs}

    dur_data = _get_dur_data()
    findings = run_rules(
        item_seqs,
        item_names,
        dur_data,
        is_elderly=req.profile.is_elderly,
        is_pregnant=req.profile.is_pregnant,
    )

    # KAERS 자료가 없으면 자동으로 빈 결과 → β·γ 컴포넌트는 0 으로 떨어진다.
    ae_df = load_ae_reports(_RAW_DIR)
    prr_results = build_prr_for_drugs(item_seqs, ae_df)
    ae_freq = ae_frequency_score(item_seqs, ae_df)

    gcn_scores = score_drugs(item_seqs)
    risk = compute_risk(
        findings,
        prr_results=prr_results,
        ae_freq=ae_freq,
        gcn_scores=gcn_scores,
    )

    drug_dicts = [
        {"item_seq": d.item_seq, "item_name": d.item_name} for d in req.drugs
    ]
    finding_dicts = [
        {"severity": f.severity, "message": f.message, "evidence": f.evidence}
        for f in findings
    ]
    user_prompt = USER_PROMPT_TEMPLATE.format(
        drug_list=render_drug_list(drug_dicts),
        age=req.profile.age,
        is_pregnant="네" if req.profile.is_pregnant else "아니오",
        conditions=", ".join(req.profile.conditions) or "없음",
        findings_text=render_findings(finding_dicts),
        risk_score=risk.score_0_100,
        band=risk.band,
    )

    try:
        llm_text = await call_llm(SYSTEM_PROMPT, user_prompt, settings)
    except LLMUnavailableError:
        llm_text = fallback_template()

    easy, detail = parse_two_paragraphs(llm_text)

    return AnalyzeResponse(
        risk=to_risk_out(risk),
        findings=to_finding_outs(findings),
        easy_summary=easy,
        detail_summary=detail,
        cautions=cautions_from_findings(findings),
        safe_alternatives=suggest_alternatives(findings, risk.band),
    )