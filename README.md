# AI Telegram Personal Brand Assistant (MVP)

## Project structure

- `bot/handlers.py` — Telegram handlers (onboarding, text/voice/image input, approval flow)
- `api/routes.py` — FastAPI health endpoint
- `services/ai_service.py` — DeepSeek text generation API calls
- `services/speech_service.py` — Whisper transcription
- `services/content_service.py` — post generation orchestration
- `db/database.py` — SQLite initialization
- `db/models.py` — repositories for users/entries/posts
- `scheduler/daily_jobs.py` — per-user daily prompts
- `config.py` — environment-based config
- `main.py` — app entrypoint (bot + API)

## Environment variables

```bash
export TELEGRAM_BOT_TOKEN="..."
export DEEPSEEK_API_KEY="..."
# Optional if you want separate key for Whisper:
export OPENAI_API_KEY="..."
export DEEPSEEK_MODEL="deepseek-chat"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export WHISPER_MODEL="whisper-1"
export DB_PATH="bloger.sqlite3"
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Notes

- GPT generation switched to **DeepSeek** via OpenAI-compatible API client (`base_url=https://api.deepseek.com`).
- Voice messages are transcribed with Whisper API.
- Publish button confirms publishing for MVP and stores generated content locally.
