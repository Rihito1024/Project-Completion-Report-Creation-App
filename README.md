# Report App (MVP)

Streamlit app to generate a PPTX report from inputs and uploaded files.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## LLM settings

The app reads environment variables (it loads `.env` automatically at startup).

Example `.env`:

```
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
GEMINI_IMAGE_MODEL=gemini-2.5-flash-image
GEMINI_IMAGE_SIZE=2K
IMAGE_PROVIDER=gemini
```

Supported providers:
- `openai`
- `anthropic`
- `gemini`

## Cloud Run

Build and deploy using the included `Dockerfile`.

## Template

The app uses `app/templates/review_template.pptx` by default. Replace it with your own template as needed, keeping shape names aligned with `app/config/slide_bindings.py`.
