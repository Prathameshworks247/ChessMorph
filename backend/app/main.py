from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Histogram

from .config import settings
from .inference import decode, interpolate, load_session
from .schemas import GenerateRequest, GenerateResponse, InterpolateRequest, InterpolateResponse

log = logging.getLogger(__name__)

_PRESETS_PATH = settings.MODEL_PATH.parent / "presets.json"

INFERENCE_LATENCY = Histogram(
    "chessmorph_inference_latency_seconds",
    "ONNX decoder inference latency",
    ["endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if not settings.MODEL_PATH.exists():
        raise RuntimeError(f"ONNX model not found at {settings.MODEL_PATH}")
    app.state.session = load_session(settings.MODEL_PATH)
    if _PRESETS_PATH.exists():
        with open(_PRESETS_PATH) as f:
            app.state.presets = json.load(f)
        log.info("Loaded %d presets from %s", len(app.state.presets), _PRESETS_PATH)
    else:
        app.state.presets = {}
        log.warning("presets.json not found at %s — run evaluate.py first", _PRESETS_PATH)
    log.info("Model loaded. Ready.")
    yield
    log.info("Shutting down.")


app = FastAPI(title="ChessMorph API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/presets")
def get_presets() -> dict[str, list[float]]:
    return app.state.presets


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    try:
        with INFERENCE_LATENCY.labels(endpoint="generate").time():
            b64 = decode(app.state.session, req.latent)
    except Exception as exc:
        log.exception("Inference error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return GenerateResponse(image=b64)


@app.post("/interpolate", response_model=InterpolateResponse)
def interpolate_route(req: InterpolateRequest) -> InterpolateResponse:
    try:
        with INFERENCE_LATENCY.labels(endpoint="interpolate").time():
            images = interpolate(app.state.session, req.latent_a, req.latent_b, req.steps)
    except Exception as exc:
        log.exception("Interpolation error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return InterpolateResponse(images=images)
