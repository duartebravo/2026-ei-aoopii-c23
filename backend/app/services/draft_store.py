from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from backend.app.models.brand import CampaignForm
from backend.app.models.post import GeneratedContent


class DraftStore:
    """Stores generated posts as local drafts before a future social integration."""

    def __init__(self, output_dir: Path) -> None:
        self.drafts_dir = output_dir / "drafts"

    def save(
        self,
        form: CampaignForm,
        content: GeneratedContent,
        image_path: str | None = None,
    ) -> Path:
        self.drafts_dir.mkdir(parents=True, exist_ok=True)
        created_at = datetime.now().isoformat(timespec="seconds")
        filename = f"draft-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        draft_path = self.drafts_dir / filename

        payload = {
            "created_at": created_at,
            "status": "draft",
            "form": asdict(form),
            "content": content.model_dump(),
            "image_path": image_path,
        }

        draft_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return draft_path
