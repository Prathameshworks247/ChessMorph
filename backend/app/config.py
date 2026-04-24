from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    MODEL_PATH: Path = Path(__file__).resolve().parents[3] / "ml" / "exports" / "decoder.onnx"
    LATENT_DIM: int = 16
    IMAGE_SIZE: int = 64
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]


settings = Settings()
