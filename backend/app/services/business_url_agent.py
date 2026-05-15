from __future__ import annotations

import ipaddress
import re
from html import unescape
from html.parser import HTMLParser
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from backend.app.models.brand import CampaignSuggestion

MAX_RETRIES = 2
RETRY_DELAYS_SECONDS = (2,)
MAX_HTML_BYTES = 250_000
MAX_CONTEXT_CHARS = 7_000
FETCH_TIMEOUT_SECONDS = 4
FALLBACK_MODEL = "gemini-2.5-flash-lite"


class BusinessUrlAgent:
    """Builds an editable campaign form from a business website."""

    def __init__(self, api_key: str | None, model: str) -> None:
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY em falta. Confirma que o ficheiro .env existe na raiz do projeto."
            )

        self.api_key = api_key
        self.model = model
        self.models = _unique([model, FALLBACK_MODEL])

    def generate(self, business_url: str) -> CampaignSuggestion:
        url = self._normalize_url(business_url)
        page_text = self._fetch_page_text_safely(url)

        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise RuntimeError(
                "Dependencia em falta. Instala o projeto com: pip install -e ."
            ) from exc

        client = genai.Client(api_key=self.api_key)
        prompt = self._build_prompt(url, page_text)
        last_error: Exception | None = None

        for model in self.models:
            try:
                response = self._generate_response(
                    client,
                    model,
                    prompt,
                    [types.Tool(url_context=types.UrlContext())],
                )
                if not page_text and not self._response_read_url(response):
                    raise RuntimeError(
                        "O Gemini nao conseguiu ler esse URL. Confirma que o site esta publico "
                        "e tenta novamente."
                    )

                return self._parse_suggestion(response)
            except Exception as exc:
                last_error = exc
                if not self._should_try_next_model(exc):
                    break

        if not page_text:
            message = self._format_generation_error(last_error) if last_error else ""
            raise RuntimeError(message or "Nao foi possivel preencher a campanha a partir do URL.")

        last_error = None
        for model in self.models:
            try:
                response = self._generate_response(client, model, prompt, None)
                return self._parse_suggestion(response)
            except Exception as exc:
                last_error = exc
                if not self._should_try_next_model(exc):
                    break

        raise RuntimeError(self._format_generation_error(last_error))

    def _generate_response(
        self,
        client: object,
        model: str,
        prompt: str,
        tools: object | None,
    ) -> object:
        config = {
            "response_mime_type": "application/json",
            "response_schema": CampaignSuggestion,
            "temperature": 0.25,
        }
        if tools:
            config["tools"] = tools

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
            except Exception as exc:
                if attempt == MAX_RETRIES or not self._is_retryable_error(exc):
                    raise

                sleep(RETRY_DELAYS_SECONDS[attempt - 1])

    def _normalize_url(self, value: str) -> str:
        url = value.strip()
        if not url:
            raise RuntimeError("Indica um URL ou escolhe preencher a campanha manualmente.")

        if "://" not in url:
            url = f"https://{url}"

        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise RuntimeError("O URL deve comecar por http:// ou https://.")

        hostname = parsed.hostname or ""
        if hostname in {"localhost", "127.0.0.1", "::1"}:
            raise RuntimeError("Usa um URL publico do negocio.")

        try:
            ip_address = ipaddress.ip_address(hostname)
        except ValueError:
            return url

        if ip_address.is_private or ip_address.is_loopback or ip_address.is_link_local:
            raise RuntimeError("Usa um URL publico do negocio.")

        return url

    def _fetch_page_text_safely(self, url: str) -> str:
        try:
            return self._fetch_page_text(url)
        except Exception:
            return ""

    def _fetch_page_text(self, url: str) -> str:
        request = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 SocialMediaAutopilot/0.1",
                "Accept": "text/html,text/plain;q=0.9,*/*;q=0.2",
                "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
            },
        )

        try:
            with urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response:
                content_type = response.headers.get("content-type", "").lower()
                is_text_page = (
                    not content_type
                    or "text/html" in content_type
                    or "text/plain" in content_type
                )
                if not is_text_page:
                    raise RuntimeError("O URL nao parece ser uma pagina web com texto analisavel.")

                raw_html = response.read(MAX_HTML_BYTES + 1)
                charset = response.headers.get_content_charset() or "utf-8"
        except HTTPError as exc:
            message = f"Nao foi possivel abrir o URL. O site respondeu com erro {exc.code}."
            raise RuntimeError(message) from exc
        except URLError as exc:
            raise RuntimeError(f"Nao foi possivel abrir o URL: {exc.reason}.") from exc
        except TimeoutError as exc:
            raise RuntimeError("O site demorou demasiado tempo a responder.") from exc

        html = raw_html[:MAX_HTML_BYTES].decode(charset, errors="replace")
        extracted_text = _extract_visible_page_text(html)
        if not extracted_text:
            raise RuntimeError("Nao foi encontrado texto suficiente para preencher a campanha.")

        return extracted_text[:MAX_CONTEXT_CHARS]

    def _parse_suggestion(self, response: object) -> CampaignSuggestion:
        if response.parsed:
            suggestion = response.parsed
        else:
            suggestion = CampaignSuggestion.model_validate_json(response.text)

        if not isinstance(suggestion, CampaignSuggestion):
            suggestion = CampaignSuggestion.model_validate(suggestion)

        return self._validate_suggestion(suggestion)

    def _validate_suggestion(self, suggestion: CampaignSuggestion) -> CampaignSuggestion:
        values = {
            "brand_name": suggestion.brand_name.strip(),
            "topic": suggestion.topic.strip(),
            "brand_voice": suggestion.brand_voice.strip(),
            "target_audience": suggestion.target_audience.strip(),
            "objective": suggestion.objective.strip(),
            "extra_notes": suggestion.extra_notes.strip(),
        }
        required_fields = ("brand_name", "topic", "brand_voice", "target_audience", "objective")
        if any(not values[field] for field in required_fields):
            raise RuntimeError(
                "O Gemini nao devolveu informacao suficiente para preencher a campanha."
            )

        return CampaignSuggestion(**values)

    def _response_read_url(self, response: object) -> bool:
        for candidate in getattr(response, "candidates", []) or []:
            metadata = getattr(candidate, "url_context_metadata", None)
            for url_metadata in getattr(metadata, "url_metadata", []) or []:
                status = getattr(url_metadata, "url_retrieval_status", None)
                if getattr(status, "value", status) == "URL_RETRIEVAL_STATUS_SUCCESS":
                    return True

        return False

    def _is_retryable_error(self, exc: Exception) -> bool:
        message = str(exc).lower()
        return (
            "503" in message
            or "unavailable" in message
            or "high demand" in message
            or "overloaded" in message
        )

    def _should_try_next_model(self, exc: Exception) -> bool:
        message = str(exc).lower()
        return self._is_retryable_error(exc) or "not found" in message or "404" in message

    def _format_generation_error(self, exc: Exception) -> str:
        message = str(exc)
        if self._is_retryable_error(exc):
            return (
                f"O modelo {self.model} esta temporariamente indisponivel ou com muita procura. "
                "Tenta novamente dentro de alguns minutos."
            )

        return f"Nao foi possivel preencher a campanha com {self.model}: {message}"

    def _build_prompt(self, url: str, page_text: str) -> str:
        page_context = page_text or (
            "Nao foi possivel extrair texto localmente. Usa o contexto por URL do Gemini. "
            "Se o URL for uma rede social com pouca informacao publica, infere apenas a partir "
            "do nome, slug e tipo de negocio visivel no URL."
        )

        return (
            "Es um agente de social media que transforma o site de um negocio num formulario "
            "inicial de campanha para Instagram.\n\n"
            "Regras obrigatorias:\n"
            "- Escrever em portugues de Portugal.\n"
            "- Preencher todos os campos de forma curta, editavel e util.\n"
            "- Usar apenas informacao presente no texto extraido ou inferencias conservadoras "
            "a partir do tipo de negocio.\n"
            "- Nao inventar precos, datas, descontos, moradas, horarios, certificacoes "
            "ou promessas.\n"
            "- Usa a ferramenta de contexto por URL para analisar a pagina indicada.\n"
            "- Se a pagina nao indicar uma campanha especifica, usar um tema inicial "
            "de apresentacao "
            "do negocio ou promocao suave do principal servico/produto.\n"
            "- Em URLs de redes sociais, usa o identificador do perfil para inferir "
            "um nome de marca provavel.\n"
            "- A voz da marca deve ser uma lista curta de adjetivos.\n"
            "- As notas adicionais devem guardar factos uteis encontrados no site e mencionar "
            "incertezas importantes.\n"
            "- Se tiveres de inferir dados a partir do URL, diz isso nas notas adicionais.\n\n"
            f"URL analisado: {url}\n\n"
            "Contexto adicional:\n"
            f"{page_context}\n"
        )


class _PageTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._important_chunks: list[str] = []
        self._body_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
            return

        if tag != "meta":
            return

        attrs_dict = {key.lower(): value or "" for key, value in attrs}
        key = attrs_dict.get("name") or attrs_dict.get("property")
        if key in {"description", "og:description", "twitter:description", "og:title"}:
            self._important_chunks.append(attrs_dict.get("content", ""))

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return

        text = _clean_text(data)
        if text:
            self._body_chunks.append(text)

    def text(self) -> str:
        chunks = self._important_chunks + self._body_chunks
        clean_chunks = []
        seen = set()
        for chunk in chunks:
            text = _clean_text(chunk)
            if not text or len(text) < 3:
                continue

            key = text.lower()
            if key in seen:
                continue

            seen.add(key)
            clean_chunks.append(text)

        return "\n".join(clean_chunks)


def _extract_visible_page_text(html: str) -> str:
    parser = _PageTextParser()
    parser.feed(html)
    return parser.text()


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value)).strip()


def _unique(values: list[str]) -> list[str]:
    result = []
    for value in values:
        if value and value not in result:
            result.append(value)

    return result
