"""Shared drug reference used across rule engines."""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class DrugRef:
    item_seq: str
    item_name: str
    ingredient_codes: frozenset[str]
