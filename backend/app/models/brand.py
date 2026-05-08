from __future__ import annotations

from pydantic import BaseModel


class CampaignForm(BaseModel):
    brand_name: str
    topic: str
    brand_voice: str
    target_audience: str
    objective: str
    extra_notes: str = ""
