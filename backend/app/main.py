from __future__ import annotations

from backend.app.config import load_settings
from backend.app.models.brand import CampaignForm
from backend.app.services.content_agent import ContentAgent
from backend.app.services.image_agent import ImageAgent


def main() -> None:
    try:
        settings = load_settings()

        print("Social Media Autopilot")
        print("Formulario para gerar texto de publicacao com Gemini\n")

        form = collect_campaign_form()

        print("\nA gerar texto da publicacao e prompt visual...")
        content = ContentAgent(
            api_key=settings.gemini_api_key,
            model=settings.gemini_text_model,
        ).generate(form)

        print("\nConteudo gerado")
        print("=" * 32)
        print(f"\nCaption:\n{content.caption}")
        print(f"\nHashtags:\n{' '.join(content.hashtags)}")
        print(f"\nCTA:\n{content.call_to_action}")
        print(f"\nTom usado:\n{content.tone_used}")
        print(f"\nPrompt visual:\n{content.image_prompt}")
        print(f"\nAlt text:\n{content.image_alt_text}")

        print("\nA gerar imagem com OpenAI...")
        image_path = ImageAgent(
            api_key=settings.openai_api_key,
            model=settings.openai_image_model,
            output_dir=settings.image_output_dir,
            size=settings.image_size,
            quality=settings.openai_image_quality,
        ).generate(content.image_prompt)

        print(f"\nImagem gerada:\n{image_path}")
    except RuntimeError as exc:
        print(f"\nErro: {exc}")
        raise SystemExit(1) from exc


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
