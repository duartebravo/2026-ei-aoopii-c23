from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen

from backend.app.models.post import GeneratedContent

INSTAGRAM_CAPTION_LIMIT = 2_200
INSTAGRAM_MIN_IMAGE_RATIO = 4 / 5
INSTAGRAM_MAX_IMAGE_RATIO = 1.91


@dataclass(frozen=True)
class InstagramPublishResult:
    media_id: str
    container_id: str
    text: str
    image_url: str


class InstagramPublisher:
    """Publishes generated content to Instagram using the Instagram Platform API."""

    def __init__(
        self,
        account_id: str | None,
        access_token: str | None,
        public_media_base_url: str | None,
        output_dir: Path,
        api_version: str = "v22.0",
        base_url: str = "https://graph.instagram.com",
        image_uploader=None,
    ) -> None:
        if not account_id:
            raise RuntimeError("INSTAGRAM_ACCOUNT_ID em falta no ficheiro .env.")
        if not access_token:
            raise RuntimeError("INSTAGRAM_ACCESS_TOKEN em falta no ficheiro .env.")

        self.account_id = account_id
        self.access_token = access_token
        self.public_media_base_url = public_media_base_url
        self.output_dir = output_dir
        self.api_version = api_version.strip().strip("/")
        self.base_url = base_url.rstrip("/")
        self.image_uploader = image_uploader

    def publish(
        self,
        content: GeneratedContent,
        image_path: str | None,
    ) -> InstagramPublishResult:
        if not image_path:
            raise RuntimeError("Gera primeiro uma imagem antes de publicar no Instagram.")

        post_text = self._build_post_text(content)
        public_image_path = self._prepare_public_image(image_path)
        image_url = self._resolve_public_image_url(public_image_path)

        try:
            container = self._post_form(
                self._endpoint("media"),
                {
                    "image_url": image_url,
                    "caption": post_text,
                    "access_token": self.access_token,
                },
            )
            container_id = str(container.get("id") or container.get("creation_id") or "")
            if not container_id:
                raise RuntimeError("A Meta nao devolveu o ID do container da publicacao.")

            published = self._post_form(
                self._endpoint("media_publish"),
                {
                    "creation_id": container_id,
                    "access_token": self.access_token,
                },
            )
            media_id = str(published.get("id") or "")
            if not media_id:
                raise RuntimeError("A Meta nao devolveu o ID da publicacao.")

        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(f"Nao foi possivel publicar no Instagram: {exc}") from exc

        return InstagramPublishResult(
            media_id=media_id,
            container_id=container_id,
            text=post_text,
            image_url=image_url,
        )

    def _build_post_text(self, content: GeneratedContent) -> str:
        hashtags = self._normalise_hashtags(content.hashtags)
        sections = [
            content.caption.strip(),
            content.call_to_action.strip(),
            " ".join(hashtags),
        ]
        text = "\n\n".join(section for section in sections if section)

        if not text:
            raise RuntimeError("A caption para Instagram esta vazia.")
        if len(text) > INSTAGRAM_CAPTION_LIMIT:
            raise RuntimeError(
                "A caption para Instagram ultrapassa o limite de "
                f"{INSTAGRAM_CAPTION_LIMIT} caracteres."
            )
        return text

    def _normalise_hashtags(self, hashtags: list[str]) -> list[str]:
        normalised = []
        for raw_tag in hashtags:
            tag = raw_tag.strip()
            if not tag:
                continue
            if not tag.startswith("#"):
                tag = f"#{tag.lstrip('#')}"
            normalised.append(tag)
        return normalised

    def _prepare_public_image(self, image_path: str) -> Path:
        source_path = Path(image_path)
        if not source_path.exists():
            raise RuntimeError(f"Imagem nao encontrada: {image_path}")

        resolved_source = source_path.resolve()
        resolved_output_dir = self.output_dir.resolve()
        if not resolved_source.is_relative_to(resolved_output_dir):
            raise RuntimeError("A imagem tem de estar dentro da pasta de outputs do projeto.")

        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError(
                "Dependencia em falta. Instala o projeto com: pip install -e ."
            ) from exc

        destination_dir = resolved_output_dir / "instagram"
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / f"{resolved_source.stem}.jpg"

        try:
            with Image.open(resolved_source) as source:
                image = self._to_rgb(source)
                width, height = image.size
                ratio = width / height
                if ratio < INSTAGRAM_MIN_IMAGE_RATIO or ratio > INSTAGRAM_MAX_IMAGE_RATIO:
                    raise RuntimeError(
                        "A imagem para Instagram deve ter proporcao entre 4:5 e 1.91:1."
                    )

                image.save(destination, format="JPEG", quality=92, optimize=True)
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Nao foi possivel preparar a imagem para o Instagram: {exc}"
            ) from exc

        return destination

    def _to_rgb(self, image):
        from PIL import Image

        if image.mode in {"RGBA", "LA"}:
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.getchannel("A"))
            return background
        return image.convert("RGB")

    def _build_public_image_url(self, image_path: Path) -> str:
        base_url = self._validated_public_media_base_url()
        relative_path = image_path.resolve().relative_to(self.output_dir.resolve()).as_posix()
        return f"{base_url}/{quote(relative_path, safe='/-._~')}"

    def _resolve_public_image_url(self, image_path: Path) -> str:
        if self.image_uploader:
            return str(self.image_uploader.upload_public_image(image_path))

        return self._build_public_image_url(image_path)

    def _validated_public_media_base_url(self) -> str:
        if not self.public_media_base_url:
            raise RuntimeError(
                "PUBLIC_MEDIA_BASE_URL em falta no ficheiro .env. "
                "Usa um URL publico que a Meta consiga abrir, por exemplo um tunnel "
                "ngrok/cloudflared apontado para /outputs."
            )

        base_url = self.public_media_base_url.rstrip("/")
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise RuntimeError("PUBLIC_MEDIA_BASE_URL tem de ser um URL absoluto http ou https.")

        hostname = parsed.hostname or ""
        if hostname in {"localhost", "127.0.0.1", "0.0.0.0", "::1"} or hostname.endswith(
            ".local"
        ):
            raise RuntimeError(
                "PUBLIC_MEDIA_BASE_URL tem de ser publico. A Meta nao consegue abrir localhost."
            )

        return base_url

    def _endpoint(self, edge: str) -> str:
        return f"{self.base_url}/{self.api_version}/{self.account_id}/{edge}"

    def _post_form(self, url: str, data: dict[str, str]) -> dict[str, object]:
        body = urlencode(data).encode("utf-8")
        request = Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "SocialMediaAutopilot/0.1",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=60) as response:
                return self._decode_json(response.read())
        except HTTPError as exc:
            detail = self._extract_error_detail(exc.read())
            raise RuntimeError(f"Instagram respondeu com erro: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(
                f"Nao foi possivel contactar a API do Instagram: {exc.reason}"
            ) from exc

    def _decode_json(self, raw_body: bytes) -> dict[str, object]:
        try:
            data = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError("A resposta do Instagram nao e JSON valido.") from exc

        if not isinstance(data, dict):
            raise RuntimeError("A resposta do Instagram tem um formato inesperado.")

        return data

    def _extract_error_detail(self, raw_body: bytes) -> str:
        try:
            data = self._decode_json(raw_body)
        except RuntimeError:
            return raw_body.decode("utf-8", errors="replace") or "erro desconhecido"

        error = data.get("error")
        if isinstance(error, dict):
            message = str(error.get("message") or "erro desconhecido")
            code = error.get("code")
            subcode = error.get("error_subcode")
            details = [message]
            if code:
                details.append(f"code {code}")
            if subcode:
                details.append(f"subcode {subcode}")
            return " / ".join(details)

        return str(data)
