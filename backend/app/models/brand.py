from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, Field


@dataclass
class CampaignForm:
    brand_name: str
    topic: str
    brand_voice: str
    target_audience: str
    objective: str
    extra_notes: str = ""


class CampaignSuggestion(BaseModel):
    brand_name: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    brand_voice: str = Field(min_length=1)
    target_audience: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    extra_notes: str = ""

    def to_campaign_form(self) -> CampaignForm:
        return CampaignForm(
            brand_name=self.brand_name.strip(),
            topic=self.topic.strip(),
            brand_voice=self.brand_voice.strip(),
            target_audience=self.target_audience.strip(),
            objective=self.objective.strip(),
            extra_notes=self.extra_notes.strip(),
        )
