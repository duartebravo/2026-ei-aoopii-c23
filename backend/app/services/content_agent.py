from __future__ import annotations

from backend.app.models.brand import CampaignForm
from backend.app.models.post import GeneratedContent


class ContentAgent:
    """Generates Instagram post text from the campaign form using Gemini."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate(self, form: CampaignForm) -> GeneratedContent:
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError(
                "Dependencia em falta. Instala o projeto com: pip install -e ."
            ) from exc

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model,
            contents=self._build_prompt(form),
            config={
                "response_mime_type": "application/json",
                "response_schema": GeneratedContent,
                "temperature": 0.4,
            },
        )

        if response.parsed:
            return response.parsed

        return GeneratedContent.model_validate_json(response.text)

    def _build_prompt(self, form: CampaignForm) -> str:
        return (
            "Es um agente de social media especializado em Instagram.\n"
            "Cria o texto de uma publicacao com base no formulario do utilizador.\n\n"
            "Regras obrigatorias:\n"
            "- Escrever em portugues de Portugal.\n"
            "- Adaptar o tom a voz da marca.\n"
            "- A caption deve ser natural, clara e pronta a publicar.\n"
            "- Usar entre 3 e 8 hashtags.\n"
            "- Cada hashtag deve comecar obrigatoriamente com #.\n"
            "- O texto para imagem deve ser curto e facil de ler.\n"
            "- Nao inventar dados, estatisticas ou promessas falsas.\n\n"
            f"Marca: {form.brand_name}\n"
            f"Tema: {form.topic}\n"
            f"Voz da marca: {form.brand_voice}\n"
            f"Publico-alvo: {form.target_audience}\n"
            f"Objetivo: {form.objective}\n"
            f"Notas adicionais: {form.extra_notes or 'sem notas adicionais'}\n"
        )
