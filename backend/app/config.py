from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[1]

_FALLBACK_CORS = "http://localhost:3000,http://127.0.0.1:3000"


def _default_model_path() -> Path:
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
    CORS_ORIGINS: str = _FALLBACK_CORS

    def cors_origins_list(self) -> list[str]:
        raw = self.CORS_ORIGINS.strip()
        if not raw:
            return _FALLBACK_CORS.split(",")
        return [o.strip() for o in raw.split(",") if o.strip()]


settings = Settings()
