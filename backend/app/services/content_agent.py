from __future__ import annotations

from time import sleep

from backend.app.models.brand import CampaignForm
from backend.app.models.post import GeneratedContent

MAX_RETRIES = 3
RETRY_DELAYS_SECONDS = (2, 5)


class ContentAgent:
    """Generates Instagram post text and an image prompt from the campaign form."""

    def __init__(self, api_key: str | None, model: str) -> None:
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY em falta. Confirma que o ficheiro .env existe na raiz do projeto."
            )

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
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = client.models.generate_content(
                    model=self.model,
                    contents=self._build_prompt(form),
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": GeneratedContent,
                        "temperature": 0.4,
                    },
                )
                break
            except Exception as exc:
                if attempt == MAX_RETRIES or not self._is_retryable_error(exc):
                    raise RuntimeError(self._format_generation_error(exc)) from exc

                sleep(RETRY_DELAYS_SECONDS[attempt - 1])

        if response.parsed:
            return response.parsed

        return GeneratedContent.model_validate_json(response.text)

    def _is_retryable_error(self, exc: Exception) -> bool:
        message = str(exc).lower()
        return (
            "503" in message
            or "unavailable" in message
            or "high demand" in message
            or "overloaded" in message
        )

    def _format_generation_error(self, exc: Exception) -> str:
        message = str(exc)
        if self._is_retryable_error(exc):
            return (
                f"O modelo {self.model} esta temporariamente indisponivel ou com muita procura. "
                "Tenta novamente dentro de alguns minutos."
            )

        return f"Nao foi possivel gerar o texto com {self.model}: {message}"

    def _build_prompt(self, form: CampaignForm) -> str:
        return (
            "Es um agente de social media especializado em Instagram.\n"
            "Cria uma publicacao e um prompt visual com base no formulario do utilizador.\n\n"
            "Regras obrigatorias:\n"
            "- Escrever em portugues de Portugal.\n"
            "- Adaptar o tom a voz da marca.\n"
            "- A caption deve ser natural, clara e pronta a publicar.\n"
            "- Usar entre 3 e 8 hashtags.\n"
            "- O call_to_action deve ser curto e alinhado com o objetivo.\n"
            "- O tone_used deve resumir o tom usado numa frase curta.\n"
            "- Nao inventar dados, estatisticas ou promessas falsas.\n\n"
            "Regras para a imagem:\n"
            "- Gerar o campo image_prompt em ingles.\n"
            "- O image_prompt deve descrever uma fotografia/visual para Instagram.\n"
            "- Usar marca, tema, voz, publico-alvo, objetivo e notas para orientar o visual.\n"
            "- A imagem nao pode conter texto, letras, palavras, legendas, logotipos, "
            "marcas de agua, interfaces, posters, embalagens com texto ou tipografia legivel.\n"
            "- O image_prompt deve focar assunto principal, contexto, composicao, luz, "
            "cores, estilo e mood.\n"
            "- O image_alt_text deve estar em portugues de Portugal e descrever a imagem "
            "para acessibilidade.\n\n"
            f"Marca: {form.brand_name}\n"
            f"Tema: {form.topic}\n"
            f"Voz da marca: {form.brand_voice}\n"
            f"Publico-alvo: {form.target_audience}\n"
            f"Objetivo: {form.objective}\n"
            f"Notas adicionais: {form.extra_notes or 'sem notas adicionais'}\n"
        )
