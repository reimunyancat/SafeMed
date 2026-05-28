from __future__ import annotations

from typing import Any, Literal, Protocol

Audience = Literal["pregnant", "elderly", "child", "adult"]


class _ProfileLike(Protocol):
    age: int
    is_pregnant: bool
    is_elderly: bool
    conditions: list[str]


_PERSONA_HEADERS: dict[Audience, str] = {
    "elderly": (
        "당신은 SafeMed 의약품 안전 도우미입니다. 65세 이상 어르신께 약물 "
        "상호작용을 설명해 드리는 역할이에요. 의학 용어는 풀어서 말씀드리고, "
        "한 문장은 짧게, 한 단락은 3–4문장으로 유지합니다."
    ),
    "pregnant": (
        "당신은 SafeMed 의약품 안전 도우미입니다. 임신 중이신 산모님께 약물의 "
        "안전성을 설명해 드리는 역할이에요. 태아 영향과 임신 안전등급(FDA·한국 "
        "등급)이 있을 경우 함께 짚어드리고, 한 문장은 짧게, 한 단락은 3–4문장으로 "
        "유지합니다."
    ),
    "child": (
        "당신은 SafeMed 의약품 안전 도우미입니다. 보호자께 영유아·소아 환자의 "
        "약물 상호작용을 설명해 드리는 역할이에요. 연령·체중 기준 용량 가능성과 "
        "소아 금기 여부를 짚어드리고, 한 문장은 짧게, 한 단락은 3–4문장으로 "
        "유지합니다."
    ),
    "adult": (
        "당신은 SafeMed 의약품 안전 도우미입니다. 일반 성인 사용자에게 약물 "
        "상호작용과 주의사항을 설명해 드리는 역할이에요. 한 문장은 짧게, 한 "
        "단락은 3–4문장으로 유지합니다."
    ),
}

_AUDIENCE_HINT: dict[Audience, str] = {
    "elderly": "(2~3문장, 65세 어르신 기준)",
    "pregnant": "(2~3문장, 임신 중인 산모 기준)",
    "child": "(2~3문장, 영유아·소아 보호자 기준)",
    "adult": "(2~3문장, 일반 성인 기준)",
}

_COMMON_RULES = (
    "\n\n규칙:\n"
    "- \"병용금기\", \"약리학\", \"상호작용\" 같은 단어는 풀어서 설명하세요.\n"
    "- 진단·처방을 직접 하지 말고 항상 \"꼭 의사·약사 선생님께 여쭤보세요\"로 마무리하세요.\n"
    "- 거짓말 금지: 모르는 약은 모른다고 말해주세요.\n"
    "- 출력은 두 단락: (1) **쉬운 요약**, (2) **자세한 설명**."
)


def select_audience(profile: _ProfileLike) -> Audience:
    if getattr(profile, "is_pregnant", False):
        return "pregnant"
    if getattr(profile, "is_elderly", False) or getattr(profile, "age", 0) >= 65:
        return "elderly"
    if getattr(profile, "age", 0) < 12:
        return "child"
    return "adult"


def build_system_prompt(profile: _ProfileLike) -> str:
    audience = select_audience(profile)
    return _PERSONA_HEADERS[audience] + _COMMON_RULES


def build_user_prompt(
    profile: _ProfileLike,
    drugs: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    risk_score: int,
    band: str,
) -> str:
    audience = select_audience(profile)
    return (
        "사용자가 함께 복용하려는 약 목록과 분석 결과입니다.\n\n"
        f"[약 목록]\n{render_drug_list(drugs)}\n\n"
        "[프로필]\n"
        f"- 나이: {profile.age}세\n"
        f"- 임신 여부: {'네' if profile.is_pregnant else '아니오'}\n"
        f"- 만성질환: {', '.join(profile.conditions) or '없음'}\n\n"
        f"[규칙 검사 결과]\n{render_findings(findings)}\n\n"
        "[종합 위험 점수]\n"
        f"{risk_score}점 / 100점 ({band})\n\n"
        "[지시]\n"
        "위 정보를 토대로 두 단락 답변을 만들어 주세요:\n"
        f"1. **쉬운 요약** {_AUDIENCE_HINT[audience]}\n"
        "2. **자세한 설명** (4~6문장, 왜 위험한지, 어떻게 해야 하는지)\n"
    )


def render_drug_list(drugs: list[dict[str, Any]]) -> str:
    return "\n".join(f"- {d['item_name']} ({d['item_seq']})" for d in drugs)


def render_findings(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return "특별히 발견된 위험 조합은 없습니다."
    lines: list[str] = []
    for f in findings:
        lines.append(
            f"- [{f['severity'].upper()}] {f['message']} → 근거: {f['evidence']}"
        )
    return "\n".join(lines)


SYSTEM_PROMPT = _PERSONA_HEADERS["elderly"] + _COMMON_RULES

USER_PROMPT_TEMPLATE = """\
사용자가 함께 복용하려는 약 목록과 분석 결과입니다.

[약 목록]
{drug_list}

[프로필]
- 나이: {age}세
- 임신 여부: {is_pregnant}
- 만성질환: {conditions}

[규칙 검사 결과]
{findings_text}

[종합 위험 점수]
{risk_score}점 / 100점 ({band})

[지시]
위 정보를 토대로 두 단락 답변을 만들어 주세요:
1. **쉬운 요약** (2~3문장, 대상자 기준)
2. **자세한 설명** (4~6문장, 왜 위험한지, 어떻게 해야 하는지)
"""