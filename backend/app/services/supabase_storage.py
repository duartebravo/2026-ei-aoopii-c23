from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class SupabaseStorageUploader:
    supabase_url: str | None
    api_key: str | None
    bucket: str
    path_prefix: str = "instagram"

    def upload_public_image(self, image_path: Path) -> str:
        if not image_path.exists():
            raise RuntimeError(f"Imagem nao encontrada: {image_path}")

        supabase_url = self._validated_supabase_url()
        api_key = self._validated_api_key()
        bucket = self._validated_bucket()
        object_path = self._build_object_path(image_path)
        upload_url = self._build_storage_url(supabase_url, "object", bucket, object_path)
        headers = self._build_upload_headers(api_key)

        request = Request(
            upload_url,
            data=image_path.read_bytes(),
            headers=headers,
            method="POST",
        )

        try:
            with urlopen(request, timeout=60) as response:
                self._decode_json(response.read())
        except HTTPError as exc:
            detail = self._extract_error_detail(exc.read())
            raise RuntimeError(f"Supabase Storage respondeu com erro: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(
                f"Nao foi possivel contactar o Supabase Storage: {exc.reason}"
            ) from exc

        return self._build_storage_url(supabase_url, "object/public", bucket, object_path)

    def _validated_supabase_url(self) -> str:
        if not self.supabase_url:
            raise RuntimeError("SUPABASE_URL em falta no ficheiro .env.")

        supabase_url = self.supabase_url.rstrip("/")
        parsed = urlparse(supabase_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise RuntimeError("SUPABASE_URL tem de ser um URL absoluto https.")

        return supabase_url

    def _validated_api_key(self) -> str:
        if not self.api_key:
            raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY em falta no ficheiro .env.")
        return self.api_key

    def _validated_bucket(self) -> str:
        bucket = self.bucket.strip()
        if not bucket:
            raise RuntimeError("SUPABASE_BUCKET em falta no ficheiro .env.")
        return bucket

    def _build_object_path(self, image_path: Path) -> str:
        prefix = self.path_prefix.strip("/")
        if prefix:
            return f"{prefix}/{image_path.name}"
        return image_path.name

    def _build_upload_headers(self, api_key: str) -> dict[str, str]:
        headers = {
            "apikey": api_key,
            "Content-Type": "image/jpeg",
            "Cache-Control": "3600",
            "x-upsert": "true",
            "User-Agent": "SocialMediaAutopilot/0.1",
        }

        if not api_key.startswith("sb_secret_"):
            headers["Authorization"] = f"Bearer {api_key}"

        return headers

    def _build_storage_url(
        self,
        supabase_url: str,
        storage_edge: str,
        bucket: str,
        object_path: str,
    ) -> str:
        encoded_bucket = quote(bucket, safe="")
        encoded_path = quote(object_path, safe="/-._~")
        return f"{supabase_url}/storage/v1/{storage_edge}/{encoded_bucket}/{encoded_path}"

    def _decode_json(self, raw_body: bytes) -> dict[str, object]:
        if not raw_body:
            return {}

        try:
            data = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError("A resposta do Supabase Storage nao e JSON valido.") from exc

        if not isinstance(data, dict):
            raise RuntimeError("A resposta do Supabase Storage tem um formato inesperado.")

        return data

    def _extract_error_detail(self, raw_body: bytes) -> str:
        try:
            data = self._decode_json(raw_body)
        except RuntimeError:
            return raw_body.decode("utf-8", errors="replace") or "erro desconhecido"

        message = data.get("message") or data.get("error") or data
        return str(message)
