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
