from __future__ import annotations

import asyncio
import logging
import os

import uvicorn
from aiogram import Bot, Dispatcher
from fastapi import FastAPI

from api.routes import router as api_router
from bot.handlers import setup_handlers
from config import load_settings
from db.database import Database
from db.models import EntryRepository, PostRepository, UserRepository
from scheduler.daily_jobs import DailyScheduler
from services.ai_service import AIService
from services.content_service import ContentService
from services.speech_service import SpeechService


async def run_bot() -> None:
    settings = load_settings()

    db = Database(settings.db_path)
    await db.init()

    users = UserRepository(db)
    entries = EntryRepository(db)
    posts = PostRepository(db)

    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()

    ai_service = AIService(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        model=settings.deepseek_model,
    )
    openai_api_key = os.getenv("OPENAI_API_KEY", settings.deepseek_api_key)
    speech_service = SpeechService(openai_api_key=openai_api_key, model=settings.whisper_model)
    content_service = ContentService(ai_service=ai_service, entries=entries, posts=posts)

    scheduler = DailyScheduler(bot=bot, users=users)
    await scheduler.start()

    dp.include_router(
        setup_handlers(
            users=users,
            entries=entries,
            posts=posts,
            content=content_service,
            speech=speech_service,
            scheduler=scheduler,
        )
    )

    await dp.start_polling(bot)


def build_api() -> FastAPI:
    app = FastAPI(title="Bloger Assistant API")
    app.include_router(api_router)
    return app


async def run_api() -> None:
    config = uvicorn.Config(build_api(), host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await asyncio.gather(run_bot(), run_api())


if __name__ == "__main__":
    asyncio.run(main())
