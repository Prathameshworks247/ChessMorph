from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[1]


def _default_model_path() -> Path:
    # Prefer decoder.onnx bundled alongside the backend package (Vercel / Docker).
    # Fall back to the monorepo ml/exports path for local dev without copying.
    local = _BACKEND_DIR / "decoder.onnx"
    if local.exists():
        return local
    return _BACKEND_DIR.parent / "ml" / "exports" / "decoder.onnx"


def _default_cors() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "")
    if raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    return ["http://localhost:3000", "http://127.0.0.1:3000"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    MODEL_PATH: Path = _default_model_path()
    LATENT_DIM: int = 16
    IMAGE_SIZE: int = 64
    CORS_ORIGINS: list[str] = _default_cors()


settings = Settings()
