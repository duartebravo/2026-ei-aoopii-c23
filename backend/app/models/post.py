from __future__ import annotations

from pydantic import BaseModel, Field


class GeneratedContent(BaseModel):
    caption: str
    caption_bluesky: str = Field(max_length=300)
    hashtags: list[str]
    call_to_action: str
    tone_used: str
    image_prompt: str
    image_alt_text: str
