from __future__ import annotations

import logging
import os

import streamlit as st
from dotenv import load_dotenv

from app.ui.step1_basic_info import render_step1
from app.ui.step2_inputs import render_step2
from app.ui.step3_review import render_step3
from app.utils.state import init_session_state


load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


st.set_page_config(page_title="案件報告書生成", layout="wide")

init_session_state()

st.title("案件報告書生成アプリ")

steps = ["Step 1: 基本情報", "Step 2: 入力", "Step 3: 確認・編集"]
step = st.radio("ステップ選択", steps, horizontal=True)

if step == steps[0]:
    render_step1()
elif step == steps[1]:
    render_step2()
else:
    render_step3()
