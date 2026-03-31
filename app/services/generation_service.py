from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any

from app.models.schemas import NormalizedInput, SlideDraft

logger = logging.getLogger(__name__)

PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


class LLMError(Exception):
    pass


def _load_prompt(filename: str) -> str:
    path = PROMPT_DIR / filename
    return path.read_text(encoding="utf-8")


def _build_context(manual_text: str, uploaded_docs: list[dict]) -> str:
    doc_snippets = []
    for doc in uploaded_docs:
        text = doc.get("extracted_text", "")
        if not text:
            continue
        snippet = text[:1500]
        doc_snippets.append(f"[{doc.get('filename')}]\n{snippet}")
    combined_docs = "\n\n".join(doc_snippets)
    return f"MANUAL_INPUT:\n{manual_text}\n\nUPLOADED_DOCS:\n{combined_docs}"


def _call_openai(prompt: str) -> str:
    try:
        from openai import OpenAI
    except Exception as exc:
        raise LLMError("OpenAI SDK not available") from exc

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMError("OPENAI_API_KEY missing")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()


def _call_anthropic(prompt: str) -> str:
    try:
        import anthropic
    except Exception as exc:
        raise LLMError("Anthropic SDK not available") from exc

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise LLMError("ANTHROPIC_API_KEY missing")

    model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=600,
        temperature=0.4,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def _call_gemini(prompt: str) -> str:
    try:
        import google.generativeai as genai
    except Exception as exc:
        raise LLMError("Gemini SDK not available") from exc

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise LLMError("GEMINI_API_KEY missing")

    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return (response.text or "").strip()


def _call_llm(prompt: str) -> str:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    logger.info("LLM call start: %s", provider)
    if provider == "openai":
        text = _call_openai(prompt)
    elif provider == "anthropic":
        text = _call_anthropic(prompt)
    elif provider == "gemini":
        text = _call_gemini(prompt)
    else:
        raise LLMError(f"Unknown provider: {provider}")
    logger.info("LLM call done: %s", provider)
    return text


def _fallback_text(manual_text: str, uploaded_docs: list[dict]) -> str:
    if manual_text.strip():
        return manual_text.strip()
    for doc in uploaded_docs:
        text = doc.get("extracted_text", "").strip()
        if text:
            return text[:400]
    return ""


def generate_slide_draft(normalized_input: NormalizedInput, project_meta: Dict[str, Any]) -> SlideDraft:
    manual = normalized_input["manual_inputs"]
    uploaded_docs = normalized_input["uploaded_docs"]
    shared_manual = manual.get("summary", "")
    author = project_meta.get("author", "")
    created_date = project_meta.get("created_date", "")
    if created_date and "-" in created_date:
        created_date = created_date.replace("-", "/")
    if author:
        author = f"作成者：{author}"
    slide4_defaults = {
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
    }
    survey_data = normalized_input.get("survey_data") or {}
    slide4_defaults.update(survey_data)

    draft: SlideDraft = {
        "slide1": {
            "project_name": project_meta.get("project_name", ""),
            "author": author,
            "created_date": created_date,
        },
        "slide2": {
            "summary": "",
            "sub_summary": "",
            "background": "",
            "challenge": "",
            "our_role": "",
        },
        "slide3": {
            "project_name": project_meta.get("project_name", ""),
            "member": "",
            "period_and_price": "",
            "project_overview": "",
            "success": "",
            "challenge": "",
            "learnings": "",
            "member_comment": "",
        },
        "slide4": slide4_defaults,
    }

    prompt_map = {
        "summary": ("slide2_summary.txt", manual.get("summary", "")),
        "sub_summary": ("slide2_sub_summary.txt", manual.get("summary", "")),
        "background": ("slide2_background.txt", manual.get("summary", "")),
        "challenge": ("slide2_challenge.txt", manual.get("summary", "")),
        "our_role": ("slide2_our_role.txt", manual.get("summary", "")),
        "member": ("slide3_member.txt", manual.get("summary", "")),
        "period_and_price": ("slide3_period_and_price.txt", manual.get("summary", "")),
        "project_overview": ("slide3_project_overview.txt", manual.get("summary", "")),
        "success": ("slide3_success.txt", manual.get("summary", "")),
        "challenge_slide3": ("slide3_challenge.txt", manual.get("summary", "")),
        "learnings": ("slide3_learnings.txt", manual.get("summary", "")),
        "member_comment": ("slide3_member_comment.txt", manual.get("summary", "")),
    }

    def assign_result(target_key: str, value: str) -> None:
        if target_key == "challenge_slide3":
            draft["slide3"]["challenge"] = value
        elif target_key in draft.get("slide2", {}):
            draft["slide2"][target_key] = value
        elif target_key in draft.get("slide3", {}):
            draft["slide3"][target_key] = value

    def run_one(target_key: str, prompt_file: str, manual_text: str) -> str:
        if not manual_text.strip():
            manual_text = shared_manual
        base_prompt = _load_prompt(prompt_file)
        context = _build_context(manual_text, uploaded_docs)
        prompt = f"{base_prompt}\n\n{context}"
        return _call_llm(prompt)

    max_workers = int(os.getenv("LLM_MAX_WORKERS", "4"))
    futures = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for key, (prompt_file, manual_text) in prompt_map.items():
            futures[executor.submit(run_one, key, prompt_file, manual_text)] = (key, manual_text)

        for future in as_completed(futures):
            key, manual_text = futures[future]
            try:
                generated = future.result()
                if not generated:
                    raise LLMError("Empty response")
                assign_result(key, generated)
            except Exception:
                logger.exception("LLM failed for %s", key)
                fallback_text = manual_text.strip() or shared_manual
                fallback = _fallback_text(fallback_text, uploaded_docs)
                assign_result(key, fallback)

    return draft
