from __future__ import annotations

import tempfile
from pathlib import Path

from aiogram import Bot
from openai import AsyncOpenAI


class SpeechService:
    def __init__(self, openai_api_key: str, model: str = "whisper-1") -> None:
        self.model = model
        self.client = AsyncOpenAI(api_key=openai_api_key)

    async def transcribe_voice(self, bot: Bot, file_id: str) -> str:
        file = await bot.get_file(file_id)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_file:
            path = Path(temp_file.name)

        await bot.download_file(file.file_path, destination=path)

        try:
            with path.open("rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                )
            return transcript.text
        finally:
            path.unlink(missing_ok=True)
