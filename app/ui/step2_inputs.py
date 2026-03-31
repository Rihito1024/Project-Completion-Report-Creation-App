from __future__ import annotations

import streamlit as st

from app.services.file_parser_service import parse_uploaded_files
from app.services.survey_service import parse_survey_file
from app.utils.files import validate_uploads
from app.utils.state import reset_generation_state


def render_step2():
    st.header("Step 2: AI生成用の入力")

    st.subheader("テキスト入力")
    st.session_state.manual_inputs["summary"] = st.text_area(
        "案件関連テキスト（議事録・メモ・Backlog/Slackのコピペなど）",
        value=st.session_state.manual_inputs.get("summary", ""),
        height=240,
    )
    st.caption("この入力は2〜3ページの文案生成に使います。必要なら後で各ボックスを編集できます。")

    st.subheader("ファイルアップロード (資料)")
    uploaded_files = st.file_uploader(
        "txt, md, csv, xlsx, docx, pdf",
        type=["txt", "md", "csv", "xlsx", "docx", "pdf"],
        accept_multiple_files=True,
    )

    st.subheader("アンケートファイル")
    survey_file = st.file_uploader(
        "CSV または Excel",
        type=["csv", "xlsx"],
        accept_multiple_files=False,
    )

    if st.button("入力を保存"):
        reset_generation_state()
        st.success("入力を保存しました")

    if st.button("ファイルを読込"):
        errors = validate_uploads(uploaded_files)
        if errors:
            for err in errors:
                st.error(err)
        else:
            st.session_state.uploaded_docs = parse_uploaded_files(uploaded_files)
            st.success("資料の読込が完了しました")

        if survey_file:
            st.session_state.survey_data = parse_survey_file(survey_file)
            st.success("アンケートの読込が完了しました")
        else:
            st.session_state.survey_data = None

    if st.session_state.uploaded_docs:
        st.info(f"読み込み済み資料: {len(st.session_state.uploaded_docs)} 件")

    if st.session_state.survey_data:
        st.info("アンケートデータを読み込み済み")
