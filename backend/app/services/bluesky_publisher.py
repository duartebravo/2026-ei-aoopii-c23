from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from backend.app.models.post import GeneratedContent

BLUESKY_TEXT_LIMIT = 300
BLUESKY_IMAGE_LIMIT_BYTES = 2_000_000


@dataclass(frozen=True)
class BlueskyPublishResult:
    uri: str
    cid: str
    text: str


class BlueskyPublisher:
    """Publishes generated content to Bluesky using the AT Protocol SDK."""

    def __init__(
        self,
        handle: str | None,
        app_password: str | None,
        service_url: str = "https://bsky.social",
    ) -> None:
        if not handle:
            raise RuntimeError("BLUESKY_HANDLE em falta no ficheiro .env.")
        if not app_password:
            raise RuntimeError("BLUESKY_APP_PASSWORD em falta no ficheiro .env.")

        self.handle = handle
        self.app_password = app_password
        self.service_url = service_url

    def publish(
        self,
        content: GeneratedContent,
        image_path: str | None,
    ) -> BlueskyPublishResult:
        try:
            from atproto import Client
        except ImportError as exc:
            raise RuntimeError(
                "Dependencia em falta. Instala o projeto com: pip install -e ."
            ) from exc

        post_text = self._build_post_text(content)
        client = Client(self.service_url)

        try:
            client.login(self.handle, self.app_password)

            if image_path:
                image_bytes = self._prepare_image(image_path)
                response = client.send_image(
                    text=post_text,
                    image=image_bytes,
                    image_alt=content.image_alt_text.strip() or "Imagem da publicacao.",
                )
            else:
                response = client.send_post(post_text)
        except Exception as exc:
            raise RuntimeError(f"Nao foi possivel publicar no Bluesky: {exc}") from exc

        return BlueskyPublishResult(
            uri=str(getattr(response, "uri", "")),
            cid=str(getattr(response, "cid", "")),
            text=post_text,
        )

    def _build_post_text(self, content: GeneratedContent) -> str:
        caption = content.caption.strip()
        call_to_action = content.call_to_action.strip()
        hashtags = self._format_hashtags(content.hashtags)

        text = self._join_parts(caption, call_to_action, hashtags)
        if len(text) <= BLUESKY_TEXT_LIMIT:
            return text

        hashtags = self._format_hashtags(content.hashtags[:3])
        text = self._fit_with_suffix(caption, self._join_parts(call_to_action, hashtags))
        if len(text) <= BLUESKY_TEXT_LIMIT:
            return text

        text = self._fit_with_suffix(caption, hashtags)
        if len(text) <= BLUESKY_TEXT_LIMIT:
            return text

        return self._truncate(caption, BLUESKY_TEXT_LIMIT)

    def _fit_with_suffix(self, caption: str, suffix: str) -> str:
        if not suffix:
            return self._truncate(caption, BLUESKY_TEXT_LIMIT)

        caption_limit = BLUESKY_TEXT_LIMIT - len(suffix) - 2
        if caption_limit < 40:
            return self._truncate(caption, BLUESKY_TEXT_LIMIT)

        return self._join_parts(self._truncate(caption, caption_limit), suffix)

    def _format_hashtags(self, hashtags: list[str]) -> str:
        cleaned = []
        for raw_tag in hashtags:
            tag = raw_tag.strip().replace(" ", "")
            if not tag:
                continue
            if not tag.startswith("#"):
                tag = f"#{tag.lstrip('#')}"
            cleaned.append(tag)
        return " ".join(cleaned)

    def _join_parts(self, *parts: str) -> str:
        return "\n\n".join(part for part in parts if part)

    def _truncate(self, text: str, limit: int) -> str:
        if len(text) <= limit:
            return text
        if limit <= 3:
            return text[:limit]
        return f"{text[: limit - 3].rstrip()}..."

    def _prepare_image(self, image_path: str) -> bytes:
        path = Path(image_path)
        if not path.exists():
            raise RuntimeError(f"Imagem nao encontrada: {image_path}")

        image_bytes = path.read_bytes()

        try:
            from PIL import Image
        except ImportError as exc:
            if len(image_bytes) <= BLUESKY_IMAGE_LIMIT_BYTES:
                return image_bytes
            raise RuntimeError(
                "Dependencia em falta. Instala o projeto com: pip install -e ."
            ) from exc

        try:
            with Image.open(path) as source:
                image = self._to_rgb(source)
                original_max_side = max(image.size)
                max_sides = (original_max_side, 1600, 1280, 1080, 900, 720)
                for max_side in dict.fromkeys(max_sides):
                    resized = image.copy()
                    resized.thumbnail((max_side, max_side))
                    for quality in (92, 88, 82, 76, 70, 64, 58, 52, 46, 40):
                        output = BytesIO()
                        resized.save(
                            output,
                            format="JPEG",
                            quality=quality,
                            optimize=True,
                        )
                        compressed = output.getvalue()
                        if len(compressed) <= BLUESKY_IMAGE_LIMIT_BYTES:
                            return compressed
        except Exception as exc:
            raise RuntimeError(f"Nao foi possivel preparar a imagem para o Bluesky: {exc}") from exc

        if len(image_bytes) <= BLUESKY_IMAGE_LIMIT_BYTES:
            return image_bytes

        raise RuntimeError(
            "A imagem continua acima do limite do Bluesky mesmo depois de comprimida."
        )

    def _to_rgb(self, image):
        from PIL import Image

        if image.mode in {"RGBA", "LA"}:
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.getchannel("A"))
            return background
        return image.convert("RGB")
