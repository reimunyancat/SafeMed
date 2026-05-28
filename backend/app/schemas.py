"""Pydantic v2 request/response schemas for /api/analyze."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["high", "medium", "low"]
Band = Literal["green", "yellow", "red"]


class DrugInput(BaseModel):
    item_seq: str = Field(..., description="MFDS item_seq")
    item_name: str = Field(..., description="Display name")


class ProfileInput(BaseModel):
    age: int = Field(..., ge=0, le=120)
    is_pregnant: bool = False
    conditions: list[str] = Field(
        default_factory=list,
        description="e.g. ['kidney', 'liver', 'diabetes']",
    )

    @property
    def is_elderly(self) -> bool:
        return self.age >= 65


class AnalyzeRequest(BaseModel):
    drugs: list[DrugInput] = Field(..., min_length=1, max_length=20)
    profile: ProfileInput


class FindingOut(BaseModel):
    kind: str
    severity: Severity
    drug_a_name: str
    drug_b_name: str | None = None
    message: str
    evidence: str


class RiskOut(BaseModel):
    score: int = Field(..., ge=0, le=100)
    band: Band
    rule_component: float
    prr_component: float
    ae_component: float
    gcn_component: float


class AnalyzeResponse(BaseModel):
    risk: RiskOut
    findings: list[FindingOut]
    easy_summary: str
    detail_summary: str
    cautions: list[str]
    safe_alternatives: list[str]
