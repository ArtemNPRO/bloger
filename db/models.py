from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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
        async with await self.db.connect() as conn:
            row = await conn.execute_fetchone(
                "SELECT id, telegram_id, preferred_time FROM users WHERE telegram_id = ?",
                (telegram_id,),
            )
            if row:
                return User(**dict(row))

            await conn.execute("INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,))
            await conn.commit()
            row = await conn.execute_fetchone(
                "SELECT id, telegram_id, preferred_time FROM users WHERE telegram_id = ?",
                (telegram_id,),
            )
            return User(**dict(row))

    async def set_preferred_time(self, telegram_id: int, preferred_time: str) -> None:
        async with await self.db.connect() as conn:
            await conn.execute(
                "UPDATE users SET preferred_time = ? WHERE telegram_id = ?",
                (preferred_time, telegram_id),
            )
            await conn.commit()

    async def list_with_time(self) -> list[User]:
        async with await self.db.connect() as conn:
            rows = await conn.execute_fetchall(
                "SELECT id, telegram_id, preferred_time FROM users WHERE preferred_time IS NOT NULL"
            )
            return [User(**dict(r)) for r in rows]

    async def by_telegram(self, telegram_id: int) -> User | None:
        async with await self.db.connect() as conn:
            row = await conn.execute_fetchone(
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
        async with await self.db.connect() as conn:
            await conn.execute(
                """
                INSERT INTO entries (user_id, raw_input, processed_text, image_file_id)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, raw_input, processed_text, image_file_id),
            )
            await conn.commit()

    async def last_processed(self, user_id: int, limit: int = 5) -> list[str]:
        async with await self.db.connect() as conn:
            rows = await conn.execute_fetchall(
                """
                SELECT processed_text FROM entries
                WHERE user_id = ? AND processed_text IS NOT NULL
                ORDER BY id DESC LIMIT ?
                """,
                (user_id, limit),
            )
            return [r[0] for r in rows if r[0]]


class PostRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    async def add(self, user_id: int, content: str) -> None:
        async with await self.db.connect() as conn:
            await conn.execute(
                "INSERT INTO posts (user_id, content) VALUES (?, ?)",
                (user_id, content),
            )
            await conn.commit()

    async def recent(self, user_id: int, limit: int = 3) -> list[str]:
        async with await self.db.connect() as conn:
            rows = await conn.execute_fetchall(
                "SELECT content FROM posts WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, limit),
            )
            return [r[0] for r in rows]
