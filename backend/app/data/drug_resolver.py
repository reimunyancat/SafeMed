"""Resolve user-facing drugs to ingredient codes via DUR cross-reference."""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import pandas as pd
import structlog

from app.data.csv_loader import DurType, load_all

log = structlog.get_logger(__name__)

_TOKEN_PATTERN = re.compile(r"[가-힣A-Za-z]+")

def _normalize_name(name: str) -> str:
    """부루펜정200밀리그램(이부프로펜) → '이부프로펜'.

    괄호 안 토큰 우선, 없으면 가장 긴 한글/영문 토큰.
    """
    if not name:
        return ""
    for parens in re.findall(r"\(([^)]+)\)", name):
        tokens = _TOKEN_PATTERN.findall(parens)
        if tokens:
            return max(tokens, key=len)
    tokens = _TOKEN_PATTERN.findall(name)
    return max(tokens, key=len) if tokens else name.strip()

class DrugResolver:
    """item_seq / item_name → ingredient_code 매핑 인덱스.

    DUR CSV 전체에서 (item_seq, ingredient_code) 와 (item_name, ingredient_code)
    조합을 모아 두 가지 역인덱스를 만든다.
    """

    def __init__(self, dur_data: dict[DurType, pd.DataFrame]) -> None:
        seq_to_codes: dict[str, set[str]] = {}
        name_to_codes: dict[str, set[str]] = {}

        for _, df in dur_data.items():
            if df.empty:
                continue
            pairs: list[tuple[str, str, str]] = []
            if "ingredient_code_a" in df.columns:
                for r in df.itertuples(index=False):
                    pairs.append((
                        getattr(r, "item_seq_a", ""),
                        getattr(r, "item_name_a", ""),
                        getattr(r, "ingredient_code_a", ""),
                    ))
                    pairs.append((
                        getattr(r, "item_seq_b", ""),
                        getattr(r, "item_name_b", ""),
                        getattr(r, "ingredient_code_b", "") if "ingredient_code_b" in df.columns else "",
                    ))
            elif "ingredient_code" in df.columns:
                for r in df.itertuples(index=False):
                    pairs.append((
                        getattr(r, "item_seq", ""),
                        getattr(r, "item_name", ""),
                        getattr(r, "ingredient_code", ""),
                    ))

            for seq, name, code in pairs:
                if not code:
                    continue
                code = str(code).strip()
                if not code:
                    continue
                if seq:
                    seq_to_codes.setdefault(str(seq).strip(), set()).add(code)
                if name:
                    key = _normalize_name(str(name))
                    if key:
                        name_to_codes.setdefault(key, set()).add(code)

        self._seq_to_codes = seq_to_codes
        self._name_to_codes = name_to_codes
        log.info(
            "drug_resolver_built",
            seq_index_size=len(seq_to_codes),
            name_index_size=len(name_to_codes),
        )

    def resolve(self, item_seq: str, item_name: str = "") -> set[str]:
        """가능한 모든 ingredient_code 반환. 못 찾으면 빈 집합."""
        codes: set[str] = set()
        if item_seq and item_seq in self._seq_to_codes:
            codes |= self._seq_to_codes[item_seq]
        if codes:
            return codes
        if not item_name:
            return codes
        key = _normalize_name(item_name)
        if not key:
            return codes
        if key in self._name_to_codes:
            return set(self._name_to_codes[key])
        for cand, cand_codes in self._name_to_codes.items():
            if cand and (cand in key or key in cand):
                codes |= cand_codes
                if len(codes) >= 8:
                    break
        return codes

@lru_cache(maxsize=4)
def get_resolver(raw_dir_str: str) -> DrugResolver:
    return DrugResolver(load_all(Path(raw_dir_str)))
