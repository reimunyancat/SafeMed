"""Korean LLM prompts — elderly-friendly tone."""
from __future__ import annotations

from typing import Any

SYSTEM_PROMPT = """\
당신은 SafeMed 의약품 안전 도우미입니다. 60세 이상 어르신께 약물 상호작용을
설명해 드리는 역할이에요. 의학 용어는 풀어서 말씀드리고, 한 문장은 짧게, 한
단락은 3–4문장으로 유지합니다.

규칙:
- "병용금기", "약리학", "상호작용" 같은 단어는 풀어서 설명하세요.
- 진단·처방을 직접 하지 말고 항상 "꼭 의사·약사 선생님께 여쥐보세요"로 마무리하세요.
- 거짓말 금지: 모르는 약은 모른다고 말씨서요.
- 출력은 두 단락: (1) **쉬운 요약**, (2) **자세한 설명**.
"""

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
1. **쉬운 요약** (2~3문장, 60세 어르신 기준)
2. **자세한 설명** (4~6문장, 왜 위험한지, 어떻게 해야 하는지)
"""


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
