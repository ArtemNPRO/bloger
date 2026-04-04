from __future__ import annotations

from dataclasses import dataclass

from db.database import Database


@dataclass(slots=True)
class User:
    id: int
    telegram_id: int
    preferred_time: str | None


class UserRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    async def get_or_create(self, telegram_id: int) -> User:
        user = await self.by_telegram(telegram_id)
        if user:
            return user

        await self.db.execute("INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,))
        created_user = await self.by_telegram(telegram_id)
        if not created_user:
            raise RuntimeError("Failed to create user")
        return created_user

    async def set_preferred_time(self, telegram_id: int, preferred_time: str) -> None:
        await self.db.execute(
            "UPDATE users SET preferred_time = ? WHERE telegram_id = ?",
            (preferred_time, telegram_id),
        )

    async def list_with_time(self) -> list[User]:
        rows = await self.db.fetchall(
            "SELECT id, telegram_id, preferred_time FROM users WHERE preferred_time IS NOT NULL"
        )
        return [User(**dict(row)) for row in rows]

    async def by_telegram(self, telegram_id: int) -> User | None:
        row = await self.db.fetchone(
            "SELECT id, telegram_id, preferred_time FROM users WHERE telegram_id = ?",
            (telegram_id,),
        )
        return User(**dict(row)) if row else None


class EntryRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    async def add(
        self,
        user_id: int,
        raw_input: str | None,
        processed_text: str | None,
        image_file_id: str | None = None,
    ) -> None:
        await self.db.execute(
            """
            INSERT INTO entries (user_id, raw_input, processed_text, image_file_id)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, raw_input, processed_text, image_file_id),
        )

    async def last_processed(self, user_id: int, limit: int = 5) -> list[str]:
        rows = await self.db.fetchall(
            """
            SELECT processed_text FROM entries
            WHERE user_id = ? AND processed_text IS NOT NULL
            ORDER BY id DESC LIMIT ?
            """,
            (user_id, limit),
        )
        return [row[0] for row in rows if row[0]]


class PostRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    async def add(self, user_id: int, content: str) -> None:
        await self.db.execute(
            "INSERT INTO posts (user_id, content) VALUES (?, ?)",
            (user_id, content),
        )

    async def recent(self, user_id: int, limit: int = 3) -> list[str]:
        rows = await self.db.fetchall(
            "SELECT content FROM posts WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        )
        return [row[0] for row in rows]
