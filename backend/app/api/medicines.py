from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import Settings, get_settings
from app.core.errors import DataFetchError, DataParseError
from app.data.cache import Cache
from app.data.fetcher import MFDSClient

log = structlog.get_logger(__name__)

router = APIRouter()


def _get_client(settings: Settings) -> MFDSClient:
    cache = Cache(settings.cache_db_path, ttl_hours=settings.cache_ttl_hours)
    return MFDSClient(settings, cache=cache)


@router.get("/medicines/search")
async def search_medicines(
    q: str = Query(..., min_length=1, max_length=100),
    settings: Settings = Depends(get_settings),
) -> list[dict]:
    client = _get_client(settings)
    try:
        data = await client.search_drug(item_name=q, num_of_rows=10)
        items = MFDSClient.parse_items(data)
    except DataFetchError as e:
        log.warning("mfds_search_unavailable", q=q, error=str(e))
        raise HTTPException(
            status_code=503,
            detail="식약처 의약품 검색 서비스를 사용할 수 없어요. 잠시 후 다시 시도해주세요.",
        ) from e
    except DataParseError as e:
        log.error("mfds_search_parse_error", q=q, error=str(e))
        raise HTTPException(
            status_code=502,
            detail="식약처 응답을 해석하지 못했어요. 관리자에게 문의해주세요.",
        ) from e

    return [
        {
            "itemSeq": it.get("itemSeq", ""),
            "itemName": it.get("itemName", ""),
            "entpName": it.get("entpName", ""),
            "efcyQesitm": it.get("efcyQesitm", ""),
            "useMethodQesitm": it.get("useMethodQesitm", ""),
            "atpnQesitm": it.get("atpnQesitm", ""),
            "intrcQesitm": it.get("intrcQesitm", ""),
        }
        for it in items
    ]