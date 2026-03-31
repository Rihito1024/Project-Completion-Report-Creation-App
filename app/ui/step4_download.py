from __future__ import annotations

import io

import streamlit as st


def render_step4():
    st.header("Step 4: ダウンロード")

    if st.session_state.pptx_bytes:
        st.download_button(
            "PPTXをダウンロード",
            data=io.BytesIO(st.session_state.pptx_bytes),
            file_name=st.session_state.pptx_filename or "report.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
    else:
        st.info("まだPPTXが生成されていません。Step 3で生成してください。")
