from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

import pandas as pd
import structlog

log = structlog.get_logger(__name__)

DurType = Literal[
    "combo",
    "elderly",
    "pregnancy",
    "age",
    "duplicate_class",
    "period",
    "dosage",
]

EXPECTED_COLUMNS: dict[DurType, list[str]] = {
    "combo": ["item_seq_a", "item_name_a", "item_seq_b", "item_name_b", "prohibit_content"],
    "elderly": ["item_seq", "item_name", "ingredient_code", "caution_content"],
    "pregnancy": ["item_seq", "item_name", "ingredient_code", "grade", "caution_content"],
    "age": ["item_seq", "item_name", "ingredient_code", "age_group", "caution_content"],
    "duplicate_class": ["item_seq", "item_name", "class_code", "class_name"],
    "period": ["item_seq", "item_name", "ingredient_code", "max_days", "caution_content"],
    "dosage": ["item_seq", "item_name", "ingredient_code", "max_dose", "unit", "caution_content"],
}

KIDS_HEADER_ALIASES: dict[str, str] = {
    "품목일련번호": "item_seq",
    "제품명": "item_name",
    "성분코드": "ingredient_code",
    "상세내용": "caution_content",
    "금기사유": "caution_content",
    "주의내용": "caution_content",
    "효능군분류번호": "class_code",
    "효능군명": "class_name",
    "품목일련번호A": "item_seq_a",
    "제품명A": "item_name_a",
    "품목일련번호B": "item_seq_b",
    "제품명B": "item_name_b",
    "금기내용": "prohibit_content",
    "임부등급": "grade",
    "특정연령군": "age_group",
    "최대투여기간": "max_days",
    "최대투여량": "max_dose",
    "단위": "unit",
    # 영문 키 (OpenAPI JSON → CSV)
    "ITEM_SEQ": "item_seq",
    "ITEM_NAME": "item_name",
    "INGR_CODE": "ingredient_code",
    "INGR_KOR_NAME": "ingredient_name",
    "PROHBT_CONTENT": "prohibit_content",
    "NOTIFICATION_DATE": "notification_date",
    "REMARK": "caution_content",
    "CLASS_CODE": "class_code",
    "CLASS_NAME": "class_name",
    "EFFECT_CODE": "class_code",
    "EFFECT_NAME": "class_name",
    "MIXTURE_ITEM_SEQ": "item_seq_b",
    "MIXTURE_ITEM_NAME": "item_name_b",
    "PREGNANT_GRADE": "grade",
    "AGE_BASE": "age_group",
    "FORM_NAME": "form_name",
    "MAX_DOSAGE": "max_dose",
    "MAX_DOSAGE_UNIT": "unit",
    "MAX_PERIOD": "max_days",
    "MAX_QTY_DESC": "caution_content",
    "MIXTURE_INGR_CODE": "ingredient_code_b",
}

DUR_FILES: dict[DurType, list[str]] = {
    "combo": ["dur_combo.csv", "한국의약품안전관리원_병용금기약물.csv"],
    "elderly": ["dur_elderly.csv", "한국의약품안전관리원_노인주의약물.csv"],
    "pregnancy": ["dur_pregnancy.csv", "한국의약품안전관리원_임부금기약물.csv"],
    "age": ["dur_age.csv", "한국의약품안전관리원_연령금기.csv"],
    "duplicate_class": [
        "dur_duplicate_class.csv",
        "한국의약품안전관리원_효능군중복주의약물.csv",
    ],
    "period": ["dur_period.csv", "한국의약품안전관리원_투여기간주의약물.csv"],
    "dosage": ["dur_dosage.csv", "한국의약품안전관리원_용량주의약물.csv"],
}


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {c: KIDS_HEADER_ALIASES.get(c.strip(), c) for c in df.columns}
    df = df.rename(columns=renamed)
    if not df.columns.duplicated().any():
        return df
    merged: dict[str, pd.Series] = {}
    for name in pd.unique(df.columns):
        sub = df.loc[:, df.columns == name]
        if sub.shape[1] == 1:
            merged[name] = sub.iloc[:, 0]
        else:
            filled = sub.replace("", pd.NA).bfill(axis=1).iloc[:, 0]
            merged[name] = filled.fillna("")
    return pd.DataFrame(merged)


def _resolve(file_dir: Path, dur_type: DurType) -> Path | None:
    for name in DUR_FILES[dur_type]:
        p = file_dir / name
        if p.exists():
            return p
    return None


def load_dur_csv(file_dir: str | Path, dur_type: DurType) -> pd.DataFrame:
    file_dir = Path(file_dir)
    target = _resolve(file_dir, dur_type)
    if target is None:
        log.info("dur_csv_missing", dir=str(file_dir), dur_type=dur_type)
        return pd.DataFrame(columns=EXPECTED_COLUMNS[dur_type])

    df: pd.DataFrame | None = None
    for enc in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            df = pd.read_csv(target, dtype=str, encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    if df is None:
        raise UnicodeDecodeError("csv", b"", 0, 0, f"cannot decode {target}")

    df = _normalise_columns(df).fillna("")
    df = df.dropna(how="all")

    # combo 전용: ingredient_code (A 측) → ingredient_code_a 로 분리
    if (
        dur_type == "combo"
        and "ingredient_code" in df.columns
        and "ingredient_code_a" not in df.columns
    ):
        df = df.rename(columns={"ingredient_code": "ingredient_code_a"})

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
    return df


def resolve_raw_dir(default: str | Path = "data/raw") -> Path:
    raw_env = os.environ.get("SAFEMED_RAW_DIR", "").strip()
    return Path(raw_env) if raw_env else Path(default)


@lru_cache(maxsize=4)
def _load_all_cached(raw_dir_str: str) -> dict[DurType, pd.DataFrame]:
    raw = Path(raw_dir_str)
    return {dur_type: load_dur_csv(raw, dur_type) for dur_type in DUR_FILES}

def load_all(raw_dir: str | Path) -> dict[DurType, pd.DataFrame]:
    raw_dir = resolve_raw_dir(raw_dir)
    return _load_all_cached(str(raw_dir.resolve()))


def has_any_real_data(data: dict[DurType, pd.DataFrame]) -> bool:
    return any(not df.empty for df in data.values())