# AI Telegram Personal Brand Assistant (MVP)

## Project structure

- `main.py` — composition root and app bootstrap (bot + API)
- `bot/handlers.py` — Telegram handlers (thin controller layer)
- `bot/presentation.py` — response formatting + inline keyboards
- `api/routes.py` — FastAPI health endpoint
- `services/assistant_service.py` — bot orchestration use-case layer
- `services/content_service.py` — post generation orchestration
- `services/ai_service.py` — DeepSeek text generation API calls
- `services/speech_service.py` — Whisper transcription
- `db/database.py` — SQLite connection helpers + schema init
- `db/models.py` — repositories for users/entries/posts
- `scheduler/daily_jobs.py` — per-user daily prompts
- `config.py` — environment-based config

## Environment variables


Use `.env` (recommended) or system env vars:

```bash
cp .env.example .env
```

Then fill:

```bash
TELEGRAM_BOT_TOKEN=...
# supported alias:
TG_API_TOKEN=...

DEEPSEEK_API_KEY=...
# optional if Whisper key differs
OPENAI_API_KEY=...

DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
WHISPER_MODEL=whisper-1
DB_PATH=bloger.sqlite3

```bash
export TELEGRAM_BOT_TOKEN="..."
export DEEPSEEK_API_KEY="..."
# Optional if you want separate key for Whisper:
export OPENAI_API_KEY="..."
export DEEPSEEK_MODEL="deepseek-chat"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export WHISPER_MODEL="whisper-1"
export DB_PATH="bloger.sqlite3"
 main
```

## Run locally

```bash

python3 -m venv .venv

python -m venv .venv
 main
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Notes


- Text generation uses **DeepSeek** via OpenAI-compatible API (`base_url=https://api.deepseek.com`).

- GPT generation switched to **DeepSeek** via OpenAI-compatible API client (`base_url=https://api.deepseek.com`).

- Voice messages are transcribed with Whisper API.
- Publish button confirms publishing for MVP and stores generated content locally.
