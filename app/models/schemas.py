from __future__ import annotations

from typing import TypedDict, List, Dict, Optional


class ProjectMeta(TypedDict):
    project_name: str
    author: str
    created_date: str


class ManualInputs(TypedDict):
    summary: str
    good_points: str
    issues: str
    learnings: str
    member_comment: str


class UploadedDoc(TypedDict):
    filename: str
    filetype: str
    extracted_text: str


class NormalizedInput(TypedDict):
    manual_inputs: ManualInputs
    uploaded_docs: List[UploadedDoc]
    survey_data: Optional[Dict]


class SlideDraft(TypedDict):
    slide1: Dict[str, str]
    slide2: Dict[str, str]
    slide3: Dict[str, str]
    slide4: Dict[str, str]
