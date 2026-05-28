from __future__ import annotations

import pandas as pd
import pytest

from app.data.csv_loader import DurType

_EMPTY_COLS: dict[str, list[str]] = {
    "combo": ["item_seq_a", "item_name_a", "item_seq_b", "item_name_b", "prohibit_content"],
    "elderly": ["item_seq", "item_name", "ingredient_code", "caution_content"],
    "pregnancy": ["item_seq", "item_name", "ingredient_code", "grade", "caution_content"],
    "age": ["item_seq", "item_name", "ingredient_code", "age_group", "caution_content"],
    "duplicate_class": ["item_seq", "item_name", "class_code", "class_name"],
    "period": ["item_seq", "item_name", "ingredient_code", "max_days", "caution_content"],
    "dosage": ["item_seq", "item_name", "ingredient_code", "max_dose", "unit", "caution_content"],
}


@pytest.fixture()
def dur_data_empty() -> dict[DurType, pd.DataFrame]:
    return {k: pd.DataFrame(columns=v) for k, v in _EMPTY_COLS.items()}


@pytest.fixture()
def dur_data_elderly_combo() -> dict[DurType, pd.DataFrame]:
    combo = pd.DataFrame(
        [
            {
                "item_seq_a": "WARFARIN-001",
                "item_name_a": "와파린정",
                "item_seq_b": "ASPIRIN-001",
                "item_name_b": "아스피린정",
                "prohibit_content": "출혈 위험 증가",
            }
        ]
    )
    elderly = pd.DataFrame(
        [
            {
                "item_seq": "WARFARIN-001",
                "item_name": "와파린정",
                "ingredient_code": "B01AA03",
                "caution_content": "고령자 출혈 위험",
            },
            {
                "item_seq": "IBUPROFEN-001",
                "item_name": "이부프로펜정",
                "ingredient_code": "M01AE01",
                "caution_content": "고령자 위장관 출혈",
            },
        ]
    )
    others = {
        k: pd.DataFrame(columns=v)
        for k, v in _EMPTY_COLS.items()
        if k not in {"combo", "elderly"}
    }
    return {"combo": combo, "elderly": elderly, **others}