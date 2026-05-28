"""Report builder + LLM summarizer (Module 3)."""
from app.report.builder import (
    cautions_from_findings,
    suggest_alternatives,
    to_finding_outs,
    to_risk_out,
)
from app.report.llm import call_llm, fallback_template, parse_two_paragraphs
from app.report.prompts import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    render_drug_list,
    render_findings,
)

__all__ = [
    "SYSTEM_PROMPT",
    "USER_PROMPT_TEMPLATE",
    "call_llm",
    "cautions_from_findings",
    "fallback_template",
    "parse_two_paragraphs",
    "render_drug_list",
    "render_findings",
    "suggest_alternatives",
    "to_finding_outs",
    "to_risk_out",
]
