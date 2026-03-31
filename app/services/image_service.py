from __future__ import annotations

import logging
import os
from io import BytesIO
from typing import Dict, Any

from google import genai
from google.genai import types

from app.models.schemas import NormalizedInput

logger = logging.getLogger(__name__)


class ImageGenerationError(Exception):
    pass


def _build_image_prompt(normalized_input: NormalizedInput, project_meta: Dict[str, Any]) -> str:
    project_name = project_meta.get("project_name", "")
    manual_summary = normalized_input["manual_inputs"].get("summary", "")

    return (
        "Generate a single clean system architecture diagram in a style similar to a draw.io or diagrams.net workflow. "
        "Create a structured high-level overview of the project or system using a left-to-right layout. "
        "Visually organize the diagram into clearly separated sections for inputs, processing, and outputs. "
        "Represent elements as simple flat boxes, containers, nodes, grouped regions, and connecting arrows. "
        "Use aligned blocks, consistent spacing, clear grouping, and precise connector flow to make the structure easy to understand. "
        "The diagram should feel schematic, technical, and organized rather than decorative or infographic-like. "
        "Style: flat vector diagram, white background, minimal shading, subtle neutral colors, thin connector lines, clean layout, professional technical documentation style. "
        "Strict constraints: no text, no labels, no letters, no numbers, no screenshots, no decorative infographic elements. "
        "The image should look like a polished architecture diagram or workflow chart made in draw.io. "
        "\n\n"
        f"Project name: {project_name}\n"
        f"Project context: {manual_summary[:1200]}"
    )


def generate_overview_image(normalized_input: NormalizedInput, project_meta: Dict[str, Any]) -> bytes:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ImageGenerationError("GEMINI_API_KEY missing")

    model = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
    image_size = os.getenv("GEMINI_IMAGE_SIZE", "2K")
    client = genai.Client(api_key=api_key)
    prompt = _build_image_prompt(normalized_input, project_meta)

    logger.info("Image generation start: %s", model)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            image_config=types.ImageConfig(image_size=image_size),
        ),
    )

    parts = None
    if hasattr(response, "parts"):
        parts = response.parts
    elif getattr(response, "candidates", None):
        parts = response.candidates[0].content.parts

    if not parts:
        raise ImageGenerationError("No image content returned")

    for part in parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            logger.info("Image generation done")
            return part.inline_data.data
        if getattr(part, "data", None):
            logger.info("Image generation done")
            return part.data

    raise ImageGenerationError("Image data not found in response")
