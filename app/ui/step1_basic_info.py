from __future__ import annotations

from datetime import date

import streamlit as st

from app.utils.state import reset_generation_state


def render_step1():
    st.header("Step 1: 基本情報")

    with st.form("basic_info_form"):
        project_name = st.text_input("案件名", value=st.session_state.project_meta.get("project_name", ""))
        author = st.text_input("作成者", value=st.session_state.project_meta.get("author", ""))
        created_date = st.date_input(
            "作成日",
            value=date.fromisoformat(st.session_state.project_meta.get("created_date", date.today().isoformat())),
        )
        submitted = st.form_submit_button("保存")

    if submitted:
        errors = []
        if not project_name.strip():
            errors.append("案件名は必須です")
        if not author.strip():
            errors.append("作成者は必須です")
        if errors:
            for err in errors:
                st.error(err)
            return

        st.session_state.project_meta = {
            "project_name": project_name.strip(),
            "author": author.strip(),
            "created_date": created_date.isoformat(),
        }
        reset_generation_state()
        st.success("保存しました")
