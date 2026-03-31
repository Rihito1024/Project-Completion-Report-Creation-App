from __future__ import annotations

from datetime import date
from typing import Dict, Any

import streamlit as st


DEFAULT_PROJECT_META = {
    "project_name": "",
    "author": "",
    "created_date": date.today().isoformat(),
}

DEFAULT_MANUAL_INPUTS = {
    "summary": "",
    "good_points": "",
    "issues": "",
    "learnings": "",
    "member_comment": "",
}

DEFAULT_SLIDE_DRAFT = {
    "slide1": {
        "project_name": "",
        "author": "",
        "created_date": "",
    },
    "slide2": {
        "summary": "",
        "sub_summary": "",
        "background": "",
        "challenge": "",
        "our_role": "",
    },
    "slide3": {
        "project_name": "",
        "member": "",
        "period_and_price": "",
        "project_overview": "",
        "success": "",
        "challenge": "",
        "learnings": "",
        "member_comment": "",
    },
    "slide4": {
        "goal_achievement": "",
        "satisfaction": "",
        "communication_load": "",
        "nps_segment": "",
        "output_quality": "",
        "technical_expertise": "",
        "business_understanding": "",
        "positive_comment": "",
        "improvement_comment": "",
        "communication_difficulty_comment": "",
    },
}


def init_session_state() -> None:
    if "project_meta" not in st.session_state:
        st.session_state.project_meta = DEFAULT_PROJECT_META.copy()
    if "manual_inputs" not in st.session_state:
        st.session_state.manual_inputs = DEFAULT_MANUAL_INPUTS.copy()
    if "uploaded_docs" not in st.session_state:
        st.session_state.uploaded_docs = []
    if "survey_data" not in st.session_state:
        st.session_state.survey_data = None
    if "normalized_input" not in st.session_state:
        st.session_state.normalized_input = None
    if "slide_draft" not in st.session_state:
        st.session_state.slide_draft = DEFAULT_SLIDE_DRAFT.copy()
    if "pptx_bytes" not in st.session_state:
        st.session_state.pptx_bytes = None
    if "pptx_filename" not in st.session_state:
        st.session_state.pptx_filename = None
    if "overview_image_bytes" not in st.session_state:
        st.session_state.overview_image_bytes = None


def reset_generation_state() -> None:
    st.session_state.normalized_input = None
    st.session_state.slide_draft = DEFAULT_SLIDE_DRAFT.copy()
    st.session_state.pptx_bytes = None
    st.session_state.pptx_filename = None
    st.session_state.overview_image_bytes = None


def merge_project_meta(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    merged = target.copy()
    merged.update({k: v for k, v in source.items() if v is not None})
    return merged
