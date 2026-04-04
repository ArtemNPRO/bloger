from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass

import uvicorn
from aiogram import Bot, Dispatcher
from fastapi import FastAPI

from api.routes import router as api_router
from bot.handlers import setup_handlers
from config import Settings, load_settings
from db.database import Database
from db.models import EntryRepository, PostRepository, UserRepository
from scheduler.daily_jobs import DailyScheduler
from services.ai_service import AIService
from services.assistant_service import AssistantService
from services.content_service import ContentService
from services.speech_service import SpeechService


@dataclass(slots=True)
class AppContext:
    settings: Settings
    bot: Bot
    dispatcher: Dispatcher
    scheduler: DailyScheduler


async def build_context() -> AppContext:
    settings = load_settings()

    db = Database(settings.db_path)
    await db.init()

    users = UserRepository(db)
    entries = EntryRepository(db)
    posts = PostRepository(db)

    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = Dispatcher()

    ai_service = AIService(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        model=settings.deepseek_model,
    )
    speech_service = SpeechService(
        openai_api_key=os.getenv("OPENAI_API_KEY", settings.deepseek_api_key),
        model=settings.whisper_model,
    )
    content_service = ContentService(ai_service=ai_service, entries=entries, posts=posts)

    scheduler = DailyScheduler(bot=bot, users=users)
    assistant = AssistantService(
        users=users,
        entries=entries,
        posts=posts,
        content=content_service,
        scheduler=scheduler,
    )

    dispatcher.include_router(setup_handlers(assistant=assistant, speech=speech_service))
    return AppContext(
        settings=settings,
        bot=bot,
        dispatcher=dispatcher,
        scheduler=scheduler,
    )


def build_api() -> FastAPI:
    app = FastAPI(title="Bloger Assistant API")
    app.include_router(api_router)
    return app


async def run_api() -> None:
    config = uvicorn.Config(build_api(), host="0.0.0.0", port=8000, log_level="info")
    await uvicorn.Server(config).serve()


async def run_bot(context: AppContext) -> None:
    await context.scheduler.start()
    await context.dispatcher.start_polling(context.bot)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    context = await build_context()
    await asyncio.gather(run_bot(context), run_api())


if __name__ == "__main__":
    asyncio.run(main())
