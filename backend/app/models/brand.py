from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CampaignForm:
    brand_name: str
    topic: str
    brand_voice: str
    target_audience: str
    objective: str
    extra_notes: str = ""
