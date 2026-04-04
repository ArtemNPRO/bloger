from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import aiosqlite


class Database:
    def __init__(self, path: str) -> None:
        self.path = path

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[aiosqlite.Connection]:
        conn = await aiosqlite.connect(self.path)
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            await conn.close()

    async def init(self) -> None:
        async with self.connection() as conn:
            await conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    preferred_time TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    raw_input TEXT,
                    processed_text TEXT,
                    image_file_id TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                );
                """
            )
            await conn.commit()

    async def fetchone(self, query: str, params: tuple[Any, ...] = ()) -> aiosqlite.Row | None:
        async with self.connection() as conn:
            return await conn.execute_fetchone(query, params)

    async def fetchall(self, query: str, params: tuple[Any, ...] = ()) -> list[aiosqlite.Row]:
        async with self.connection() as conn:
            return await conn.execute_fetchall(query, params)

    async def execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        async with self.connection() as conn:
            await conn.execute(query, params)
            await conn.commit()
