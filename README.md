# Report App (MVP)

入力内容とアップロードしたファイルからPPTXの報告書を生成するStreamlitアプリです。

## ローカルで起動

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## LLM設定

アプリは環境変数を参照します（起動時に `.env` を自動で読み込みます）。

`.env` の例:

```
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
GEMINI_IMAGE_MODEL=gemini-2.5-flash-image
GEMINI_IMAGE_SIZE=2K
IMAGE_PROVIDER=gemini
```

対応プロバイダ:
- `openai`
- `anthropic`
- `gemini`

## Cloud Run

同梱の `Dockerfile` を使ってビルド・デプロイできます。

## テンプレート

デフォルトでは `app/templates/review_template.pptx` を使用します。必要に応じて差し替えてください（`app/config/slide_bindings.py` と形状名が一致している必要があります）。
