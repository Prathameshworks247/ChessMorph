from __future__ import annotations

from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[1]

_FALLBACK_CORS = ["http://localhost:3000", "http://127.0.0.1:3000"]


def _default_model_path() -> Path:
    # Prefer decoder.onnx bundled alongside the backend package (Vercel / Docker).
    # Fall back to the monorepo ml/exports path for local dev without copying.
    local = _BACKEND_DIR / "decoder.onnx"
    if local.exists():
        return local
    return _BACKEND_DIR.parent / "ml" / "exports" / "decoder.onnx"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
    )

    MODEL_PATH: Path = _default_model_path()
    LATENT_DIM: int = 16
    IMAGE_SIZE: int = 64
    CORS_ORIGINS: list[str] = _FALLBACK_CORS

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v: object) -> list[str]:
        if isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                return _FALLBACK_CORS
            return [o.strip() for o in stripped.split(",") if o.strip()]
        return v  # already a list (e.g. from default or JSON env var)


settings = Settings()
