from __future__ import annotations

import os
from typing import Iterable

MAX_FILE_SIZE_MB = 10
MAX_FILE_COUNT = 5


def bytes_to_mb(size_bytes: int) -> float:
    return size_bytes / (1024 * 1024)


def validate_uploads(files: Iterable) -> list[str]:
    errors: list[str] = []
    if not files:
        return errors
    files = list(files)
    if len(files) > MAX_FILE_COUNT:
        errors.append(f"Uploaded {len(files)} files; limit is {MAX_FILE_COUNT}.")
    for f in files:
        size_mb = bytes_to_mb(getattr(f, "size", 0))
        if size_mb > MAX_FILE_SIZE_MB:
            errors.append(f"{f.name}: {size_mb:.1f} MB exceeds {MAX_FILE_SIZE_MB} MB limit.")
    return errors


def safe_filename(name: str) -> str:
    safe = "".join(ch for ch in name if ch.isalnum() or ch in ("-", "_"))
    return safe or "report"


def build_pptx_filename(project_name: str, yyyymm: str) -> str:
    base = safe_filename(project_name)
    return f"{yyyymm}_{base}_report.pptx"


def get_extension(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    return ext.lower().lstrip(".")
