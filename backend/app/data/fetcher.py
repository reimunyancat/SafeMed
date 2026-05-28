"""MFDS DrbEasyDrugInfoService client.

CRITICAL: when MFDS_KEY_IS_URL_ENCODED=true, the serviceKey is already encoded
(contains %2F, %3D). It MUST be appended as a raw query-string segment so httpx
doesn't re-encode it. Other params go through urlencode as usual.
"""
from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import httpx
import structlog

from app.core.config import Settings
from app.core.errors import DataFetchError, DataParseError
from app.data.cache import Cache

log = structlog.get_logger(__name__)

DEFAULT_TIMEOUT = httpx.Timeout(20.0, connect=8.0)
DEFAULT_RETRY = 2


class MFDSClient:
    def __init__(self, settings: Settings, cache: Cache | None = None) -> None:
        self.settings = settings
        self.cache = cache

    def _build_url(self, path: str, params: dict[str, Any]) -> str:
        key = self.settings.mfds_service_key
        if not key:
            raise DataFetchError("MFDS_SERVICE_KEY not configured")
        other = {k: v for k, v in params.items() if k != "serviceKey"}
        qs = urlencode(other, doseq=True)
        base = f"{self.settings.mfds_base_url.rstrip('/')}{path}"
        if self.settings.mfds_key_is_url_encoded:
            # Append key as raw segment; httpx will not double-encode.
            return f"{base}?serviceKey={key}" + (f"&{qs}" if qs else "")
        return f"{base}?{urlencode({'serviceKey': key, **other}, doseq=True)}"

    async def _get_json(self, url: str) -> dict[str, Any]:
        last_err: Exception | None = None
        for attempt in range(DEFAULT_RETRY + 1):
            try:
                async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                    resp = await client.get(url, headers={"Accept": "application/json"})
                resp.raise_for_status()
                try:
                    return resp.json()
                except ValueError as e:
                    raise DataParseError(f"Non-JSON response from {url[:80]}") from e
            except (httpx.HTTPError, DataParseError) as e:
                last_err = e
                log.warning("mfds_request_failed", attempt=attempt, error=str(e))
        raise DataFetchError(f"MFDS request failed after retries: {last_err}")

    async def search_drug(
        self,
        *,
        item_name: str | None = None,
        item_seq: str | None = None,
        page_no: int = 1,
        num_of_rows: int = 20,
    ) -> dict[str, Any]:
        cache_key = f"search:{item_name}:{item_seq}:{page_no}:{num_of_rows}"
        if self.cache:
            cached = self.cache.get("mfds.drug", cache_key)
            if cached is not None:
                return cached

        params: dict[str, Any] = {
            "type": "json",
            "pageNo": page_no,
            "numOfRows": num_of_rows,
        }
        if item_name:
            params["itemName"] = item_name
        if item_seq:
            params["itemSeq"] = item_seq

        url = self._build_url("/DrbEasyDrugInfoService/getDrbEasyDrugList", params)
        data = await self._get_json(url)
        if self.cache:
            self.cache.set("mfds.drug", cache_key, data)
        return data

    @staticmethod
    def parse_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Pull item list from MFDS response envelope, normalising the shape."""
        try:
            body = payload["response"]["body"]
            items = body.get("items", [])
            if isinstance(items, dict) and "item" in items:
                items = items["item"]
            if isinstance(items, dict):
                items = [items]
            return list(items) if items else []
        except (KeyError, TypeError) as e:
            raise DataParseError(f"Unexpected MFDS payload shape: {e}") from e
