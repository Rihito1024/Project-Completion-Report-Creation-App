from __future__ import annotations

import io
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

from app.services.input_service import build_normalized_input
from app.services.generation_service import generate_slide_draft
from app.services.image_service import generate_overview_image, ImageGenerationError
from app.services.pptx_service import render_pptx
from app.utils.files import build_pptx_filename


TEMPLATE_PATH = str(Path(__file__).resolve().parents[1] / "templates" / "review_template.pptx")


def _render_slide_card(title: str, fields: dict):
    with st.container(border=True):
        st.markdown(f"### {title}")
        for label, key in fields.items():
            value = st.session_state.slide_draft.get(title.lower(), {}).get(key, "")
            st.session_state.slide_draft[title.lower()][key] = st.text_area(label, value=value, key=f"{title}_{key}")


def _ensure_slide_keys():
    if "slide1" not in st.session_state.slide_draft:
        st.session_state.slide_draft["slide1"] = {}
    if "slide2" not in st.session_state.slide_draft:
        st.session_state.slide_draft["slide2"] = {}
    if "slide3" not in st.session_state.slide_draft:
        st.session_state.slide_draft["slide3"] = {}
    if "slide4" not in st.session_state.slide_draft:
        st.session_state.slide_draft["slide4"] = {}


def render_step3():
    st.header("Step 3: 生成結果の確認・編集")
    _ensure_slide_keys()
    meta = st.session_state.project_meta
    author_text = meta.get("author", "")
    if author_text:
        author_text = f"作成者：{author_text}"
    created_text = meta.get("created_date", "")
    if created_text and "-" in created_text:
        created_text = created_text.replace("-", "/")
    if not st.session_state.slide_draft["slide1"].get("project_name"):
        st.session_state.slide_draft["slide1"]["project_name"] = meta.get("project_name", "")
    if not st.session_state.slide_draft["slide1"].get("author"):
        st.session_state.slide_draft["slide1"]["author"] = author_text
    if not st.session_state.slide_draft["slide1"].get("created_date"):
        st.session_state.slide_draft["slide1"]["created_date"] = created_text

    col_left, col_right = st.columns([3, 1])
    with col_left:
        if st.button("AI文案を生成"):
            normalized = build_normalized_input(
                st.session_state.manual_inputs,
                st.session_state.uploaded_docs,
                st.session_state.survey_data,
            )
            st.session_state.normalized_input = normalized
            st.session_state.slide_draft = generate_slide_draft(normalized, st.session_state.project_meta)
            st.success("生成しました")

    with col_right:
        btn_left, btn_right = st.columns(2)
        with btn_left:
            if st.button("PPTX出力"):
                try:
                    output_path = os.path.join("/tmp", "report.pptx")
                    image_bytes = st.session_state.overview_image_bytes
                    if image_bytes is None:
                        provider = os.getenv("IMAGE_PROVIDER", "gemini").lower()
                        try:
                            if provider != "gemini":
                                raise ImageGenerationError(f"Unsupported IMAGE_PROVIDER: {provider}")
                            normalized = st.session_state.normalized_input or build_normalized_input(
                                st.session_state.manual_inputs,
                                st.session_state.uploaded_docs,
                                st.session_state.survey_data,
                            )
                            st.session_state.normalized_input = normalized
                            image_bytes = generate_overview_image(normalized, st.session_state.project_meta)
                            st.session_state.overview_image_bytes = image_bytes
                            st.info("概要画像を生成しました")
                        except ImageGenerationError as exc:
                            st.warning(f"概要画像の生成に失敗しました: {exc}")
                        except Exception as exc:
                            st.warning(f"概要画像の生成に失敗しました: {exc}")
                    render_pptx(
                        st.session_state.slide_draft,
                        TEMPLATE_PATH,
                        output_path,
                        image_bytes=image_bytes,
                    )
                    with open(output_path, "rb") as f:
                        st.session_state.pptx_bytes = f.read()
                    project_name = st.session_state.project_meta.get("project_name", "report")
                    yyyymm = datetime.now().strftime("%Y%m")
                    st.session_state.pptx_filename = build_pptx_filename(project_name, yyyymm)
                    st.success("PPTXを生成しました")
                except Exception as exc:
                    st.error(f"PPTX生成に失敗しました: {exc}")
        with btn_right:
            has_pptx = st.session_state.pptx_bytes is not None
            st.download_button(
                "ダウンロード",
                data=io.BytesIO(st.session_state.pptx_bytes or b""),
                file_name=st.session_state.pptx_filename or "report.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                disabled=not has_pptx,
            )
        if not st.session_state.pptx_bytes:
            st.caption("PPTX出力後にダウンロードできます。")

    st.subheader("Slide 1")
    with st.container(border=True):
        st.session_state.slide_draft["slide1"]["project_name"] = st.text_area(
            "案件名", value=st.session_state.slide_draft["slide1"].get("project_name", ""), key="s1_project_name"
        )
        st.session_state.slide_draft["slide1"]["author"] = st.text_area(
            "作成者", value=st.session_state.slide_draft["slide1"].get("author", ""), key="s1_author"
        )
        st.session_state.slide_draft["slide1"]["created_date"] = st.text_area(
            "作成日", value=st.session_state.slide_draft["slide1"].get("created_date", ""), key="s1_created_date"
        )

    st.subheader("Slide 2")
    with st.container(border=True):
        st.session_state.slide_draft["slide2"]["summary"] = st.text_area(
            "プロジェクト概要", value=st.session_state.slide_draft["slide2"].get("summary", ""), key="s2_summary"
        )
        st.session_state.slide_draft["slide2"]["sub_summary"] = st.text_area(
            "サブサマリ", value=st.session_state.slide_draft["slide2"].get("sub_summary", ""), key="s2_sub_summary"
        )
        st.session_state.slide_draft["slide2"]["background"] = st.text_area(
            "背景", value=st.session_state.slide_draft["slide2"].get("background", ""), key="s2_background"
        )
        st.session_state.slide_draft["slide2"]["challenge"] = st.text_area(
            "課題", value=st.session_state.slide_draft["slide2"].get("challenge", ""), key="s2_challenge"
        )
        st.session_state.slide_draft["slide2"]["our_role"] = st.text_area(
            "当社の役割", value=st.session_state.slide_draft["slide2"].get("our_role", ""), key="s2_our_role"
        )

    st.subheader("Slide 3")
    with st.container(border=True):
        st.session_state.slide_draft["slide3"]["project_name"] = st.text_area(
            "案件名", value=st.session_state.slide_draft["slide3"].get("project_name", ""), key="s3_project_name"
        )
        st.session_state.slide_draft["slide3"]["member"] = st.text_area(
            "メンバー", value=st.session_state.slide_draft["slide3"].get("member", ""), key="s3_member"
        )
        st.session_state.slide_draft["slide3"]["period_and_price"] = st.text_area(
            "期間・金額", value=st.session_state.slide_draft["slide3"].get("period_and_price", ""), key="s3_period_and_price"
        )
        st.session_state.slide_draft["slide3"]["project_overview"] = st.text_area(
            "プロジェクト概要", value=st.session_state.slide_draft["slide3"].get("project_overview", ""), key="s3_project_overview"
        )
        st.session_state.slide_draft["slide3"]["success"] = st.text_area(
            "成功要因", value=st.session_state.slide_draft["slide3"].get("success", ""), key="s3_success"
        )
        st.session_state.slide_draft["slide3"]["challenge"] = st.text_area(
            "課題", value=st.session_state.slide_draft["slide3"].get("challenge", ""), key="s3_challenge"
        )
        st.session_state.slide_draft["slide3"]["learnings"] = st.text_area(
            "学び / 今後への共有", value=st.session_state.slide_draft["slide3"].get("learnings", ""), key="s3_learnings"
        )
        st.session_state.slide_draft["slide3"]["member_comment"] = st.text_area(
            "メンバーからの一言", value=st.session_state.slide_draft["slide3"].get("member_comment", ""), key="s3_member_comment"
        )

    st.subheader("Slide 4")
    with st.container(border=True):
        for key, label in [
            ("goal_achievement", "ゴール達成度"),
            ("satisfaction", "満足度"),
            ("communication_load", "やり取り負荷"),
            ("nps_segment", "NPS区分"),
            ("output_quality", "アウトプット品質"),
            ("technical_expertise", "技術的専門性"),
            ("business_understanding", "推進/提案/ビジネス理解"),
            ("positive_comment", "良かったところや感想"),
            ("improvement_comment", "気になったところや改善点"),
            ("communication_difficulty_comment", "やり取りで難しさを感じたところ"),
        ]:
            st.session_state.slide_draft["slide4"][key] = st.text_area(
                label, value=st.session_state.slide_draft["slide4"].get(key, ""), key=f"s4_{key}"
            )

    # Download button is shown in the right column.
