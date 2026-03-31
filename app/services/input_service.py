from __future__ import annotations

from typing import Dict, Any, List

from app.models.schemas import NormalizedInput


def build_normalized_input(
    manual_inputs: Dict[str, str],
    uploaded_docs: List[Dict[str, Any]],
    survey_data: Dict[str, Any] | None,
) -> NormalizedInput:
    return {
        "manual_inputs": {
            "summary": manual_inputs.get("summary", ""),
            "good_points": manual_inputs.get("good_points", ""),
            "issues": manual_inputs.get("issues", ""),
            "learnings": manual_inputs.get("learnings", ""),
            "member_comment": manual_inputs.get("member_comment", ""),
        },
        "uploaded_docs": uploaded_docs,
        "survey_data": survey_data,
    }
