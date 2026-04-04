from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot

from db.models import UserRepository


class DailyScheduler:
    def __init__(self, bot: Bot, users: UserRepository) -> None:
        self.bot = bot
        self.users = users
        self.scheduler = AsyncIOScheduler(timezone="UTC")

    async def start(self) -> None:
        for user in await self.users.list_with_time():
            if not user.preferred_time:
                continue
            hour, minute = map(int, user.preferred_time.split(":"))
            self.scheduler.add_job(
                self._send_daily_prompt,
                CronTrigger(hour=hour, minute=minute),
                args=[user.telegram_id],
                id=f"user-{user.telegram_id}",
                replace_existing=True,
            )
        self.scheduler.start()

    async def refresh_user_job(self, telegram_id: int, preferred_time: str) -> None:
        hour, minute = map(int, preferred_time.split(":"))
        self.scheduler.add_job(
            self._send_daily_prompt,
            CronTrigger(hour=hour, minute=minute),
            args=[telegram_id],
            id=f"user-{telegram_id}",
            replace_existing=True,
        )

    async def _send_daily_prompt(self, telegram_id: int) -> None:
        await self.bot.send_message(
            telegram_id,
            "Что интересного произошло сегодня?\nЧто ты понял(а) или чему научился(ась)?",
        )
