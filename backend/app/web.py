from __future__ import annotations

from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.app.config import load_settings
from backend.app.models.brand import CampaignForm
from backend.app.models.post import GeneratedContent
from backend.app.services.business_url_agent import BusinessUrlAgent
from backend.app.services.content_agent import ContentAgent
from backend.app.services.draft_store import DraftStore
from backend.app.services.image_agent import ImageAgent

APP_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"

settings = load_settings()
settings.image_output_dir.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Social Media Autopilot")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/outputs", StaticFiles(directory=settings.image_output_dir), name="outputs")


class CampaignPayload(BaseModel):
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


class ImagePayload(BaseModel):
    image_prompt: str = Field(min_length=1)


class BusinessUrlPayload(BaseModel):
    business_url: str = Field(min_length=1)


class DraftPayload(BaseModel):
    form: CampaignPayload
    content: GeneratedContent
    image_path: str | None = None


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    html = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.post("/api/analyze-business-url")
def analyze_business_url(payload: BusinessUrlPayload) -> dict[str, object]:
    current_settings = load_settings()
    try:
        suggestion = BusinessUrlAgent(
            api_key=current_settings.gemini_api_key,
            model=current_settings.gemini_text_model,
        ).generate(payload.business_url)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"form": suggestion.model_dump()}


@app.post("/api/generate-content")
def generate_content(payload: CampaignPayload) -> dict[str, object]:
    current_settings = load_settings()
    try:
        content = ContentAgent(
            api_key=current_settings.gemini_api_key,
            model=current_settings.gemini_text_model,
        ).generate(payload.to_campaign_form())
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"content": content.model_dump()}


@app.post("/api/generate-image")
def generate_image(payload: ImagePayload) -> dict[str, str]:
    current_settings = load_settings()
    filename = f"generated-post-image-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"

    try:
        image_path = ImageAgent(
            api_key=current_settings.openai_api_key,
            model=current_settings.openai_image_model,
            output_dir=current_settings.image_output_dir,
            size=current_settings.image_size,
            quality=current_settings.openai_image_quality,
        ).generate(payload.image_prompt.strip(), filename=filename)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "image_path": str(image_path),
        "image_url": f"/outputs/{quote(filename)}?v={datetime.now().timestamp()}",
    }


@app.post("/api/save-draft")
def save_draft(payload: DraftPayload) -> dict[str, str]:
    current_settings = load_settings()
    draft_path = DraftStore(current_settings.image_output_dir).save(
        form=payload.form.to_campaign_form(),
        content=payload.content,
        image_path=payload.image_path,
    )
    return {"draft_path": str(draft_path)}


def main() -> None:
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError("Dependencia em falta. Instala o projeto com: pip install -e .") from exc

    uvicorn.run("backend.app.web:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
