from __future__ import annotations

from openai import AsyncOpenAI


class AIService:
    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def generate_posts(
        self,
        user_input: str,
        recent_entries: list[str],
        recent_posts: list[str],
    ) -> list[str]:
        prompt = self._build_prompt(user_input, recent_entries, recent_posts)
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.9,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You create personal-brand social posts. Write naturally, specific, and personal. "
                        "Avoid AI clichés and generic statements. "
                        "Each post must follow hook -> body -> takeaway."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content or ""
        parts = [p.strip() for p in content.split("\n\n") if p.strip()]
        return parts[:3] if parts else [content]

    @staticmethod
    def _build_prompt(user_input: str, recent_entries: list[str], recent_posts: list[str]) -> str:
        entries_block = "\n".join(f"- {e}" for e in recent_entries) or "- none"
        posts_block = "\n".join(f"- {p}" for p in recent_posts) or "- none"

        return (
            "Create 3 social media post variations based on the user update below.\n"
            "Styles: 1) storytelling 2) short punchy 3) reflective.\n"
            "Output format exactly:\n"
            "POST 1:\n...\n\nPOST 2:\n...\n\nPOST 3:\n...\n\n"
            f"Today input:\n{user_input}\n\n"
            f"Recent entries:\n{entries_block}\n\n"
            f"Recent posts for tone memory:\n{posts_block}\n"
        )
