from __future__ import annotations

import io
import logging
from typing import Dict, Any

import pandas as pd

from app.config.survey_field_map import SURVEY_FIELD_MAP, NUMERIC_FIELDS, TEXT_FIELDS
from app.utils.files import get_extension

logger = logging.getLogger(__name__)


def _read_survey_frame(data: bytes, ext: str) -> pd.DataFrame:
    if ext == "csv":
        return pd.read_csv(io.BytesIO(data))
    return pd.read_excel(io.BytesIO(data))


def _find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for col in df.columns:
        if col in candidates:
            return col
    for cand in candidates:
        for col in df.columns:
            if str(col).strip().lower() == str(cand).strip().lower():
                return col
    return None


def _summarize_text(values: list[str]) -> str:
    cleaned = [v.strip() for v in values if isinstance(v, str) and v.strip()]
    if not cleaned:
        return ""
    unique = []
    for v in cleaned:
        if v not in unique:
            unique.append(v)
    return "\n".join(unique[:5])


def parse_survey_file(uploaded_file) -> Dict[str, Any]:
    if not uploaded_file:
        return {}

    ext = get_extension(uploaded_file.name)
    logger.info("Survey read start: %s", uploaded_file.name)
    try:
        data = uploaded_file.getvalue()
        df = _read_survey_frame(data, ext)
    except Exception:
        logger.exception("Survey read failed: %s", uploaded_file.name)
        return {}

    result: Dict[str, Any] = {}
    for field, candidates in SURVEY_FIELD_MAP.items():
        col = _find_column(df, candidates)
        if not col:
            result[field] = ""
            continue
        series = df[col].dropna()
        if series.empty:
            result[field] = ""
            continue
        if field in NUMERIC_FIELDS:
            numeric = pd.to_numeric(series, errors="coerce").dropna()
            if numeric.empty:
                result[field] = ""
            else:
                result[field] = f"?? {numeric.mean():.2f}"
        elif field in TEXT_FIELDS:
            result[field] = _summarize_text(series.astype(str).tolist())
        else:
            result[field] = str(series.iloc[0])

    logger.info("Survey read done: %s", uploaded_file.name)
    return result
