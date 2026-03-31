from __future__ import annotations

import io
import logging
from typing import List

import pandas as pd
from docx import Document
from pypdf import PdfReader

from app.utils.files import get_extension

logger = logging.getLogger(__name__)


def _read_text_file(data: bytes) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp932", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="ignore")


def _read_csv(data: bytes) -> str:
    df = pd.read_csv(io.BytesIO(data))
    return df.to_string(index=False)


def _read_xlsx(data: bytes) -> str:
    df = pd.read_excel(io.BytesIO(data))
    return df.to_string(index=False)


def _read_docx(data: bytes) -> str:
    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs)


def _read_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages)


def parse_uploaded_files(files) -> List[dict]:
    docs: List[dict] = []
    if not files:
        return docs

    for f in files:
        filename = f.name
        ext = get_extension(filename)
        logger.info("File read start: %s", filename)
        try:
            data = f.getvalue()
            if ext in ("txt", "md"):
                text = _read_text_file(data)
            elif ext == "csv":
                text = _read_csv(data)
            elif ext in ("xlsx", "xls"):
                text = _read_xlsx(data)
            elif ext == "docx":
                text = _read_docx(data)
            elif ext == "pdf":
                text = _read_pdf(data)
            else:
                text = ""
            docs.append({
                "filename": filename,
                "filetype": ext,
                "extracted_text": text.strip(),
            })
            logger.info("File read done: %s", filename)
        except Exception:
            logger.exception("File read failed: %s", filename)
            docs.append({
                "filename": filename,
                "filetype": ext,
                "extracted_text": "",
            })
    return docs
