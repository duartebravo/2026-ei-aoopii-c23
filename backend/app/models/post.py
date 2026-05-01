from __future__ import annotations

from pydantic import BaseModel, field_validator


class GeneratedContent(BaseModel):
    caption: str
    hashtags: list[str]
    image_title: str
    image_body: str
    call_to_action: str
    tone_used: str

    @field_validator("hashtags", mode="before")
    @classmethod
    def normalize_hashtags(cls, value: object) -> object:
        if not isinstance(value, list):
            return value

        normalized = []
        for hashtag in value:
            if not isinstance(hashtag, str):
                normalized.append(hashtag)
                continue

            clean_hashtag = hashtag.strip()
            if clean_hashtag and not clean_hashtag.startswith("#"):
                clean_hashtag = f"#{clean_hashtag}"
            normalized.append(clean_hashtag)

        return normalized
