"""Medicine search endpoint — proxies MFDS DrbEasyDrugInfoService."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.config import Settings, get_settings
from app.core.errors import DataFetchError
from app.data.cache import Cache
from app.data.fetcher import MFDSClient

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
    except DataFetchError:
        return []
    items = MFDSClient.parse_items(data)
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
