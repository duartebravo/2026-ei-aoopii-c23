from __future__ import annotations

import base64
from pathlib import Path


class ImageAgent:
    """Generates a post image from a visual prompt using OpenAI image models."""

    def __init__(
        self,
        api_key: str | None,
        model: str,
        output_dir: Path,
        size: str,
        quality: str,
    ) -> None:
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY em falta. Confirma que o ficheiro .env existe na raiz do projeto."
            )

        self.api_key = api_key
        self.model = model
        self.output_dir = output_dir
        self.size = size
        self.quality = quality

    def generate(self, prompt: str, filename: str = "generated-post-image.png") -> Path:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "Dependencia em falta. Instala o projeto com: pip install -e ."
            ) from exc

        client = OpenAI(api_key=self.api_key)
        try:
            response = client.images.generate(
                model=self.model,
                prompt=prompt,
                size=self.size,
                quality=self.quality,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Nao foi possivel gerar a imagem com {self.model}: {exc}"
            ) from exc

        if not response.data or not response.data[0].b64_json:
            raise RuntimeError("A API da OpenAI nao devolveu nenhuma imagem.")

        image_bytes = base64.b64decode(response.data[0].b64_json)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / filename
        output_path.write_bytes(image_bytes)
        return output_path
