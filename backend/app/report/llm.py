from __future__ import annotations

from typing import Any

import httpx
import structlog

from app.core.config import Settings
from app.core.errors import LLMUnavailableError

log = structlog.get_logger(__name__)

TIMEOUT = httpx.Timeout(60.0, connect=10.0)


async def call_llm(
    system_prompt: str, user_prompt: str, settings: Settings
) -> str:
    provider = settings.llm_provider
    if provider == "nim":
        return await _call_nim(system_prompt, user_prompt, settings)
    if provider == "upstage":
        return await _call_upstage(system_prompt, user_prompt, settings)
    if provider == "ollama":
        return await _call_ollama(system_prompt, user_prompt, settings)
    if provider == "none":
        return fallback_template()
    raise LLMUnavailableError(f"Unknown LLM_PROVIDER: {provider}")


async def _post_chat(
    url: str, headers: dict[str, str], payload: dict[str, Any]
) -> str:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as e:
        log.warning("llm_request_failed", url=url, error=str(e))
        raise LLMUnavailableError(f"LLM request failed: {e}") from e

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as e:
        raise LLMUnavailableError(f"Unexpected LLM response shape: {e}") from e


async def _call_nim(system: str, user: str, settings: Settings) -> str:
    if not settings.nim_api_key:
        raise LLMUnavailableError("NIM_API_KEY not configured")
    return await _post_chat(
        f"{settings.nim_base_url.rstrip('/')}/chat/completions",
        {
            "Authorization": f"Bearer {settings.nim_api_key}",
            "Accept": "application/json",
        },
        {
            "model": settings.nim_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
            "max_tokens": 900,
            "stream": False,
        },
    )


async def _call_upstage(system: str, user: str, settings: Settings) -> str:
    if not settings.upstage_api_key:
        raise LLMUnavailableError("UPSTAGE_API_KEY not configured")
    return await _post_chat(
        "https://api.upstage.ai/v1/solar/chat/completions",
        {
            "Authorization": f"Bearer {settings.upstage_api_key}",
            "Accept": "application/json",
        },
        {
            "model": settings.upstage_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
        },
    )


async def _call_ollama(system: str, user: str, settings: Settings) -> str:
    return await _post_chat(
        f"{settings.ollama_base_url.rstrip('/')}/v1/chat/completions",
        {"Accept": "application/json"},
        {
            "model": settings.ollama_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
            "stream": False,
        },
    )


def fallback_template() -> str:
    """Returned when LLM is unreachable or disabled."""
    return (
        "**쉬운 요약**\n\n"
        "약을 함께 드시기 전에 의사·약사 선생님께 꼭 여쭤보세요. "
        "특히 위험 점수가 높은 조합은 다른 약으로 바꿀 수 있는지 상의하시는 게 안전해요.\n\n"
        "**자세한 설명**\n\n"
        "AI 요약 기능이 비활성화 상태라 자세한 설명을 자동 생성할 수 없어요. "
        "각 약의 효능·주의사항은 약 설명서를 직접 확인하시고, "
        "여러 약을 동시에 드시는 경우에는 약사 선생님께 복용 일정과 함께 보여드리세요. "
        "본 서비스의 점수는 참고용이며 의료적 진단·처방을 대체하지 않습니다."
    )


def parse_two_paragraphs(text: str) -> tuple[str, str]:
    """Split the LLM output into (easy_summary, detail_summary)."""
    if "**자세한 설명**" in text:
        parts = text.split("**자세한 설명**", 1)
        easy = parts[0].replace("**쉬운 요약**", "").strip()
        detail = parts[1].strip()
        return easy, detail
    if "\n\n" in text:
        easy, _, detail = text.partition("\n\n")
        return easy.strip(), detail.strip()
    return text.strip(), ""