from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.app.config import load_settings
from backend.app.models.brand import CampaignForm
from backend.app.models.post import GeneratedContent
from backend.app.services.content_agent import ContentAgent

PROJECT_ROOT = Path(__file__).resolve().parents[2]

app = FastAPI(title="Social Media Autopilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def web_app() -> FileResponse:
    return FileResponse(PROJECT_ROOT / "index.html")


@app.get("/styles.css", include_in_schema=False)
def styles() -> FileResponse:
    return FileResponse(PROJECT_ROOT / "styles.css", media_type="text/css")


@app.post("/api/generate-post", response_model=GeneratedContent)
def generate_post(form: CampaignForm) -> GeneratedContent:
    settings = load_settings()

    if not settings.gemini_api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY nao configurada.")

    try:
        return ContentAgent(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
        ).generate(form)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erro ao gerar conteudo: {exc}") from exc


def main() -> None:
    settings = load_settings()

    print("Social Media Autopilot")
    print("Formulario para gerar texto de publicacao com Gemini\n")

    form = collect_campaign_form()
    content = ContentAgent(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
    ).generate(form)

    print("\nConteudo gerado")
    print("=" * 32)
    print(f"\nCaption:\n{content.caption}")
    print(f"\nHashtags:\n{' '.join(content.hashtags)}")
    print(f"\nTexto para imagem:\n{content.image_title}\n{content.image_body}")
    print(f"\nCTA:\n{content.call_to_action}")
    print(f"\nTom usado:\n{content.tone_used}")


def collect_campaign_form() -> CampaignForm:
    return CampaignForm(
        brand_name=ask_required("Nome da marca: "),
        topic=ask_required("Tema do post: "),
        brand_voice=ask_required("Voz da marca: "),
        target_audience=ask_required("Publico-alvo: "),
        objective=ask_required("Objetivo do post: "),
        extra_notes=input("Notas adicionais (opcional): ").strip(),
    )


def ask_required(label: str) -> str:
    while True:
        value = input(label).strip()
        if value:
            return value
        print("Este campo e obrigatorio.")


if __name__ == "__main__":
    main()
