from __future__ import annotations

from db.models import EntryRepository, PostRepository, User, UserRepository
from scheduler.daily_jobs import DailyScheduler
from services.content_service import ContentService


class AssistantService:
    def __init__(
        self,
        users: UserRepository,
        entries: EntryRepository,
        posts: PostRepository,
        content: ContentService,
        scheduler: DailyScheduler,
    ) -> None:
        self.users = users
        self.entries = entries
        self.posts = posts
        self.content = content
        self.scheduler = scheduler

    async def ensure_user(self, telegram_id: int) -> User:
        return await self.users.get_or_create(telegram_id)

    async def set_daily_time(self, telegram_id: int, hhmm: str) -> None:
        await self.users.set_preferred_time(telegram_id, hhmm)
        await self.scheduler.refresh_user_job(telegram_id, hhmm)

    async def process_user_input(
        self,
        telegram_id: int,
        processed_text: str,
        raw_input: str | None,
        image_file_id: str | None = None,
    ) -> list[str]:
        user = await self.users.get_or_create(telegram_id)
        await self.entries.add(
            user_id=user.id,
            raw_input=raw_input,
            processed_text=processed_text,
            image_file_id=image_file_id,
        )
        return await self.content.generate_variations(user.id, processed_text)

    async def store_published(self, telegram_id: int, content: str) -> None:
        user = await self.users.get_or_create(telegram_id)
        await self.posts.add(user.id, content)
