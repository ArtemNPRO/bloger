from __future__ import annotations

from aiogram.utils.keyboard import InlineKeyboardBuilder


def build_posts_keyboard() -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Publish", callback_data="publish")
    keyboard.button(text="Regenerate", callback_data="regenerate")
    keyboard.adjust(2)
    return keyboard


def format_posts(posts: list[str], limit: int = 3) -> str:
    prepared_posts = posts[:limit]
    return "\n\n".join(
        [f"POST {index + 1}:\n{post}" for index, post in enumerate(prepared_posts)]
    )
