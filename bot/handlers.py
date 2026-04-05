from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.presentation import build_posts_keyboard, format_posts
from services.assistant_service import AssistantService
from services.speech_service import SpeechService

_TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def setup_handlers(assistant: AssistantService, speech: SpeechService) -> Router:
    router = Router()

    @router.message(Command("start"))
    async def start(message: Message) -> None:
        await assistant.ensure_user(message.from_user.id)
        await message.answer("Привет! Укажи удобное время для ежедневного вопроса в формате HH:MM (UTC).")

    @router.message(F.text)
    async def handle_text(message: Message) -> None:
        telegram_id = message.from_user.id
        text = (message.text or "").strip()

        if _TIME_RE.fullmatch(text):
            await assistant.set_daily_time(telegram_id, text)
            await message.answer(f"Отлично, буду писать каждый день в {text} UTC.")
            return

        variations = await assistant.process_user_input(
            telegram_id=telegram_id,
            raw_input=text,
            processed_text=text,
        )
        await message.answer(format_posts(variations), reply_markup=build_posts_keyboard().as_markup())

    @router.message(F.voice)
    async def handle_voice(message: Message) -> None:
        telegram_id = message.from_user.id
        transcribed = await speech.transcribe_voice(message.bot, message.voice.file_id)

        variations = await assistant.process_user_input(
            telegram_id=telegram_id,
            raw_input="[voice]",
            processed_text=transcribed,
        )
        await message.answer(format_posts(variations), reply_markup=build_posts_keyboard().as_markup())

    @router.message(F.photo)
    async def handle_photo(message: Message) -> None:
        telegram_id = message.from_user.id
        image_file_id = message.photo[-1].file_id
        caption = message.caption or "[image uploaded]"

        variations = await assistant.process_user_input(
            telegram_id=telegram_id,
            raw_input=caption,
            processed_text=caption,
            image_file_id=image_file_id,
        )
        await message.answer(format_posts(variations), reply_markup=build_posts_keyboard().as_markup())

    @router.callback_query(F.data == "publish")
    async def publish(callback: CallbackQuery) -> None:
        if callback.message and callback.message.text:
            await assistant.store_published(callback.from_user.id, callback.message.text)
        await callback.answer("Опубликовано (MVP: подтверждение)")

    @router.callback_query(F.data == "regenerate")
    async def regenerate(callback: CallbackQuery) -> None:
        await callback.answer("Отправь новый текст/голос/картинку для перегенерации")

    return router
