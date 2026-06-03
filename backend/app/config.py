from __future__ import annotations

from dataclasses import dataclass
from os import environ, getenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    app_env: str
    gemini_api_key: str | None
    gemini_text_model: str
    openai_api_key: str | None
    openai_image_model: str
    openai_image_quality: str
    image_size: str
    image_output_dir: Path
    telegram_bot_token: str | None
    bluesky_handle: str | None
    bluesky_app_password: str | None
    bluesky_service_url: str
    instagram_account_id: str | None
    instagram_access_token: str | None
    instagram_api_version: str
    instagram_base_url: str
    public_media_base_url: str | None
    supabase_url: str | None
    supabase_service_role_key: str | None
    supabase_bucket: str


def load_settings() -> Settings:
    load_env_file(PROJECT_ROOT / ".env")

    return Settings(
        app_env=getenv("APP_ENV", "development"),
        gemini_api_key=getenv("GEMINI_API_KEY") or None,
        gemini_text_model=getenv("GEMINI_TEXT_MODEL", getenv("GEMINI_MODEL", "gemini-2.5-flash")),
        openai_api_key=getenv("OPENAI_API_KEY") or None,
        openai_image_model=getenv("OPENAI_IMAGE_MODEL", "gpt-image-2"),
        openai_image_quality=getenv("OPENAI_IMAGE_QUALITY", "medium"),
        image_size=getenv("IMAGE_SIZE", "1024x1280"),
        image_output_dir=resolve_project_path(getenv("IMAGE_OUTPUT_DIR", "outputs")),
        telegram_bot_token=getenv("TELEGRAM_BOT_TOKEN") or None,
        bluesky_handle=getenv("BLUESKY_HANDLE") or None,
        bluesky_app_password=getenv("BLUESKY_APP_PASSWORD") or None,
        bluesky_service_url=getenv("BLUESKY_SERVICE_URL", "https://bsky.social"),
        instagram_account_id=getenv("INSTAGRAM_ACCOUNT_ID") or None,
        instagram_access_token=getenv("INSTAGRAM_ACCESS_TOKEN") or None,
        instagram_api_version=getenv("INSTAGRAM_API_VERSION", "v22.0"),
        instagram_base_url=getenv("INSTAGRAM_BASE_URL", "https://graph.instagram.com"),
        public_media_base_url=getenv("PUBLIC_MEDIA_BASE_URL") or None,
        supabase_url=getenv("SUPABASE_URL") or None,
        supabase_service_role_key=(
            getenv("SUPABASE_SERVICE_ROLE_KEY") or getenv("SUPABASE_SECRET_KEY") or None
        ),
        supabase_bucket=getenv("SUPABASE_BUCKET", "instagram-posts"),
    )


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def resolve_project_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path
