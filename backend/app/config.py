from __future__ import annotations

from dataclasses import dataclass
from os import environ, getenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    app_env: str
    gemini_api_key: str | None
    gemini_model: str


def load_settings() -> Settings:
    load_env_file(PROJECT_ROOT / ".env")

    return Settings(
        app_env=getenv("APP_ENV", "development"),
        gemini_api_key=getenv("GEMINI_API_KEY") or None,
        gemini_model=getenv("GEMINI_MODEL", "gemini-2.5-pro"),
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
