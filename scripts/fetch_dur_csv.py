from __future__ import annotations

import asyncio
import csv
import sys
from pathlib import Path
from urllib.parse import quote

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.core.config import get_settings  # noqa: E402

DUR_BASE = "https://apis.data.go.kr/1471000/DURPrdlstInfoService03"
PAGE_SIZE = 500
MAX_PAGES = 2000

ENDPOINTS: list[tuple[str, str]] = [
    ("dur_combo.csv",           "getUsjntTabooInfoList03"),
    ("dur_elderly.csv",         "getOdsnAtentInfoList03"),
    ("dur_pregnancy.csv",       "getPwnmTabooInfoList03"),
    ("dur_age.csv",             "getSpcifyAgrdeTabooInfoList03"),
    ("dur_duplicate_class.csv", "getEfcyDplctInfoList03"),
    ("dur_period.csv",          "getMdctnPdAtentInfoList03"),
    ("dur_dosage.csv",          "getCpctyAtentInfoList03"),
]

OK_CODES = {"00", "0", "NORMAL_CODE", "NORMAL SERVICE."}


def _build_url(endpoint: str, page: int, key: str, key_is_encoded: bool) -> str:
    common = f"pageNo={page}&numOfRows={PAGE_SIZE}&type=json"
    if key_is_encoded:
        return f"{DUR_BASE}/{endpoint}?serviceKey={key}&{common}"
    return f"{DUR_BASE}/{endpoint}?serviceKey={quote(key, safe='')}&{common}"


def _extract(payload):
    resp = payload.get("response") if isinstance(payload, dict) else None
    resp = resp or payload or {}
    header = resp.get("header") or {}
    body = resp.get("body") or {}
    code = header.get("resultCode") or header.get("RESULT_CODE") or ""
    msg = header.get("resultMsg") or header.get("RESULT_MSG") or ""
    raw_items = body.get("items")
    rows: list[dict] = []
    if isinstance(raw_items, dict):
        inner = raw_items.get("item")
        if isinstance(inner, list):
            rows = [r for r in inner if isinstance(r, dict)]
        elif isinstance(inner, dict):
            rows = [inner]
    elif isinstance(raw_items, list):
        rows = [r for r in raw_items if isinstance(r, dict)]
    total = body.get("totalCount") or body.get("total_count") or 0
    try:
        total = int(total)
    except (TypeError, ValueError):
        total = 0
    return str(code), str(msg), rows, total


async def _fetch_endpoint(
    client: httpx.AsyncClient,
    filename: str,
    endpoint: str,
    key: str,
    key_is_encoded: bool,
) -> list[dict]:
    out: list[dict] = []
    for page in range(1, MAX_PAGES + 1):
        url = _build_url(endpoint, page, key, key_is_encoded)
        try:
            r = await client.get(url, headers={"Accept": "application/json"})
        except httpx.HTTPError as e:
            print(f"  ! HTTP error on page {page}: {e}", flush=True)
            return out
        if r.status_code != 200:
            print(f"  ! HTTP {r.status_code} on page {page}", flush=True)
            print(f"    body[:200]: {r.text[:200]}", flush=True)
            return out
        try:
            payload = r.json()
        except ValueError:
            print(f"    body[:300]: {r.text[:300]}", flush=True)
            return out
        code, msg, rows, total = _extract(payload)
        if code and code not in OK_CODES:
            print(f"  ! resultCode={code} msg={msg}", flush=True)
            return out
        if page == 1:
            print(f"  · totalCount={total}", flush=True)
        out.extend(rows)
        if len(rows) < PAGE_SIZE:
            return out
    return out


def _write_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = sorted({k for r in rows for k in r.keys()})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})


async def _amain() -> int:
    settings = get_settings()
    key = (settings.mfds_service_key or "").strip()
    if not key:
        print(
            "ERROR: MFDS_SERVICE_KEY 가 backend/.env 에 비어 있어요.",
            file=sys.stderr,
        )
        return 1

    encoded = settings.mfds_key_is_url_encoded
    print(
        f"[fetch_dur_csv] 키 인식 OK (len={len(key)}, url_encoded={encoded})",
        flush=True,
    )
    out_dir = Path(__file__).resolve().parents[1] / "data" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    timeout = httpx.Timeout(60.0, connect=10.0)
    saved = 0
    failed: list[str] = []
    async with httpx.AsyncClient(timeout=timeout) as client:
        for idx, (filename, endpoint) in enumerate(ENDPOINTS, 1):
            print(
                f"\n[{idx}/{len(ENDPOINTS)}] {filename} ({endpoint})",
                flush=True,
            )
            rows = await _fetch_endpoint(client, filename, endpoint, key, encoded)
            if not rows:
                failed.append(filename)
                continue
            _write_csv(out_dir / filename, rows)
            print(f"  OK saved {len(rows)} rows → data/raw/{filename}", flush=True)
            saved += 1

    print(f"\n[fetch_dur_csv] 완료 — {saved}/{len(ENDPOINTS)} 파일 저장", flush=True)
    if failed:
        print("  실패: " + ", ".join(failed), flush=True)
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(_amain()))


if __name__ == "__main__":
    main()