from __future__ import annotations

import logging
import re

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.models import EntryRepository, PostRepository, UserRepository
from scheduler.daily_jobs import DailyScheduler
from services.content_service import ContentService
from services.speech_service import SpeechService

router = Router()
logger = logging.getLogger(__name__)

_TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def _posts_keyboard() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="Publish", callback_data="publish")
    kb.button(text="Regenerate", callback_data="regenerate")
    kb.adjust(2)
    return kb


def setup_handlers(
    users: UserRepository,
    entries: EntryRepository,
    posts: PostRepository,
    content: ContentService,
    speech: SpeechService,
    scheduler: DailyScheduler,
) -> Router:
    @router.message(Command("start"))
    async def start(message: Message) -> None:
        await users.get_or_create(message.from_user.id)
        await message.answer("Привет! Укажи удобное время для ежедневного вопроса в формате HH:MM (UTC).")

    @router.message(F.text)
    async def handle_text(message: Message) -> None:
        telegram_id = message.from_user.id
        user = await users.get_or_create(telegram_id)

        text = (message.text or "").strip()
        if _TIME_RE.fullmatch(text):
            await users.set_preferred_time(telegram_id, text)
            await scheduler.refresh_user_job(telegram_id, text)
            await message.answer(f"Отлично, буду писать каждый день в {text} UTC.")
            return

        await entries.add(user.id, raw_input=text, processed_text=text)
        variations = await content.generate_variations(user.id, text)

        formatted = "\n\n".join(
            [f"POST {idx + 1}:\n{post}" for idx, post in enumerate(variations[:3])]
        )
        await message.answer(formatted, reply_markup=_posts_keyboard().as_markup())

    @router.message(F.voice)
    async def handle_voice(message: Message) -> None:
        telegram_id = message.from_user.id
        user = await users.get_or_create(telegram_id)

        voice_file_id = message.voice.file_id
        transcribed = await speech.transcribe_voice(message.bot, voice_file_id)
        await entries.add(user.id, raw_input="[voice]", processed_text=transcribed)

        variations = await content.generate_variations(user.id, transcribed)
        formatted = "\n\n".join(
            [f"POST {idx + 1}:\n{post}" for idx, post in enumerate(variations[:3])]
        )
        await message.answer(formatted, reply_markup=_posts_keyboard().as_markup())

    @router.message(F.photo)
    async def handle_photo(message: Message) -> None:
        telegram_id = message.from_user.id
        user = await users.get_or_create(telegram_id)
        file_id = message.photo[-1].file_id
        caption = message.caption or "[image uploaded]"

        await entries.add(
            user.id,
            raw_input=caption,
            processed_text=caption,
            image_file_id=file_id,
        )

        variations = await content.generate_variations(user.id, caption)
        formatted = "\n\n".join(
            [f"POST {idx + 1}:\n{post}" for idx, post in enumerate(variations[:3])]
        )
        await message.answer(formatted, reply_markup=_posts_keyboard().as_markup())

    @router.callback_query(F.data == "publish")
    async def publish(callback: CallbackQuery) -> None:
        if callback.message and callback.message.text:
            user = await users.get_or_create(callback.from_user.id)
            await posts.add(user.id, callback.message.text)
        await callback.answer("Опубликовано (MVP: подтверждение)")

    @router.callback_query(F.data == "regenerate")
    async def regenerate(callback: CallbackQuery) -> None:
        await callback.answer("Отправь новый текст/голос/картинку для перегенерации")

    return router
