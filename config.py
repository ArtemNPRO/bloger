from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load local .env first, then allow real environment to override values.
load_dotenv()


@dataclass(slots=True)
class Settings:
    telegram_bot_token: str
    deepseek_api_key: str
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    whisper_model: str = "whisper-1"
    db_path: str = "bloger.sqlite3"



def load_settings() -> Settings:
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TG_API_TOKEN", "")
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")

    if not telegram_bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN (or TG_API_TOKEN) is required")
    if not deepseek_api_key:
        raise ValueError("DEEPSEEK_API_KEY is required")

    return Settings(
        telegram_bot_token=telegram_bot_token,
        deepseek_api_key=deepseek_api_key,
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        whisper_model=os.getenv("WHISPER_MODEL", "whisper-1"),
        db_path=os.getenv("DB_PATH", "bloger.sqlite3"),
    )
