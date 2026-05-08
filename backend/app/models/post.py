from __future__ import annotations

from pydantic import BaseModel


class GeneratedContent(BaseModel):
    caption: str
    hashtags: list[str]
    call_to_action: str
    tone_used: str
    image_prompt: str
    image_alt_text: str
