from __future__ import annotations

import base64
import io
import logging
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image

log = logging.getLogger(__name__)


def load_session(model_path: Path) -> ort.InferenceSession:
    sess = ort.InferenceSession(
        str(model_path),
        providers=["CPUExecutionProvider"],
    )
    log.info("ONNX session loaded from %s", model_path)
    return sess


def decode(session: ort.InferenceSession, latent: list[float]) -> str:
    """Run decoder, return base64-encoded PNG string."""
    z = np.array(latent, dtype=np.float32).reshape(1, 16)
    output = session.run(["generated_image"], {"latent_vector": z})[0]
    # output shape: (1, 1, 64, 64), values in [0, 1]
    img_arr = (output[0, 0] * 255).clip(0, 255).astype(np.uint8)
    img = Image.fromarray(img_arr, mode="L")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def interpolate(
    session: ort.InferenceSession,
    latent_a: list[float],
    latent_b: list[float],
    steps: int,
) -> list[str]:
    """Linear interpolation between two latents, return list of base64 PNGs."""
    a = np.array(latent_a, dtype=np.float32)
    b = np.array(latent_b, dtype=np.float32)
    images: list[str] = []
    for t in np.linspace(0, 1, steps):
        z = ((1 - t) * a + t * b).tolist()
        images.append(decode(session, z))
    return images
