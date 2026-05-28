"""SQLite key/value cache with namespace + TTL.

Used by MFDSClient and any other adapter that wants to memoize API responses.
The DB file is created lazily on first write.
"""
from __future__ import annotations

import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class Cache:
    def __init__(self, db_path: str | Path, ttl_hours: int = 24) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl_hours * 3600
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn() as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS kv (
                    namespace TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    ts REAL NOT NULL,
                    PRIMARY KEY (namespace, key)
                )
                """
            )

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def get(self, namespace: str, key: str) -> Any | None:
        with self._conn() as c:
            row = c.execute(
                "SELECT value, ts FROM kv WHERE namespace=? AND key=?",
                (namespace, key),
            ).fetchone()
        if not row:
            return None
        value, ts = row
        if time.time() - ts > self.ttl:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    def set(self, namespace: str, key: str, value: Any) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT OR REPLACE INTO kv (namespace, key, value, ts) VALUES (?,?,?,?)",
                (namespace, key, json.dumps(value, ensure_ascii=False), time.time()),
            )

    def clear(self, namespace: str | None = None) -> int:
        with self._conn() as c:
            if namespace:
                cur = c.execute("DELETE FROM kv WHERE namespace=?", (namespace,))
            else:
                cur = c.execute("DELETE FROM kv")
            return cur.rowcount
