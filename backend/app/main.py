from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .inference import decode, interpolate, load_session
from .schemas import GenerateRequest, GenerateResponse, InterpolateRequest, InterpolateResponse

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if not settings.MODEL_PATH.exists():
        raise RuntimeError(f"ONNX model not found at {settings.MODEL_PATH}")
    app.state.session = load_session(settings.MODEL_PATH)
    log.info("Model loaded. Ready.")
    yield
    log.info("Shutting down.")


app = FastAPI(title="ChessMorph API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    try:
        b64 = decode(app.state.session, req.latent)
    except Exception as exc:
        log.exception("Inference error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return GenerateResponse(image=b64)


@app.post("/interpolate", response_model=InterpolateResponse)
def interpolate_route(req: InterpolateRequest) -> InterpolateResponse:
    try:
        images = interpolate(app.state.session, req.latent_a, req.latent_b, req.steps)
    except Exception as exc:
        log.exception("Interpolation error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return InterpolateResponse(images=images)
