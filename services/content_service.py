from __future__ import annotations

from db.models import EntryRepository, PostRepository
from services.ai_service import AIService


class ContentService:
    def __init__(
        self,
        ai_service: AIService,
        entries: EntryRepository,
        posts: PostRepository,
    ) -> None:
        self.ai_service = ai_service
        self.entries = entries
        self.posts = posts

    async def generate_variations(self, user_id: int, processed_text: str) -> list[str]:
        recent_entries = await self.entries.last_processed(user_id=user_id)
        recent_posts = await self.posts.recent(user_id=user_id)
        return await self.ai_service.generate_posts(
            user_input=processed_text,
            recent_entries=recent_entries,
            recent_posts=recent_posts,
        )
