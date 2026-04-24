from __future__ import annotations

from pydantic import BaseModel, field_validator


class GenerateRequest(BaseModel):
    latent: list[float]

    @field_validator("latent")
    @classmethod
    def validate_length(cls, v: list[float]) -> list[float]:
        if len(v) != 16:
            raise ValueError(f"latent must have exactly 16 elements, got {len(v)}")
        return v


class GenerateResponse(BaseModel):
    image: str  # base64-encoded PNG


class InterpolateRequest(BaseModel):
    latent_a: list[float]
    latent_b: list[float]
    steps: int = 8

    @field_validator("latent_a", "latent_b")
    @classmethod
    def validate_length(cls, v: list[float]) -> list[float]:
        if len(v) != 16:
            raise ValueError(f"latent must have exactly 16 elements, got {len(v)}")
        return v


class InterpolateResponse(BaseModel):
    images: list[str]  # base64-encoded PNGs
