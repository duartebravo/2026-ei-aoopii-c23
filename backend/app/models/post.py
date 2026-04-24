from __future__ import annotations

from pydantic import BaseModel


class GeneratedContent(BaseModel):
    caption: str
    hashtags: list[str]
    image_title: str
    image_body: str
    call_to_action: str
    tone_used: str
