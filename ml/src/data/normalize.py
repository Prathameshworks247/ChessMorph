from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
from PIL import Image
import yaml

log = logging.getLogger(__name__)


def load_config(config_path: Path) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def normalize_array(alpha: np.ndarray, size: int = 64, padding: int = 4) -> np.ndarray:
    """Crop to bounding box of non-zero pixels, resize back to `size` with `padding` px border."""
    rows = np.any(alpha > 0, axis=1)
    cols = np.any(alpha > 0, axis=0)

    if not rows.any():
        return alpha

    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]

    cropped = alpha[rmin:rmax + 1, cmin:cmax + 1]

    inner = size - 2 * padding
    img = Image.fromarray((cropped * 255).astype(np.uint8))
    img = img.resize((inner, inner), Image.LANCZOS)

    canvas = np.zeros((size, size), dtype=np.float32)
    canvas[padding:padding + inner, padding:padding + inner] = np.array(img) / 255.0
    return canvas


def normalize_all(cfg: dict, ml_root: Path) -> int:
    rendered_root = ml_root / cfg["paths"]["rendered"]
    size = cfg["data"]["image_size"]
    padding = cfg["data"]["padding_px"]

    count = 0
    for npy_file in sorted(rendered_root.rglob("*.npy")):
        alpha = np.load(npy_file)
        normalized = normalize_array(alpha, size=size, padding=padding)
        np.save(npy_file, normalized)
        count += 1
        log.debug("Normalized %s", npy_file)

    log.info("Normalized %d arrays", count)
    return count


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ml_root = Path(__file__).resolve().parents[2]
    cfg = load_config(ml_root / "configs" / "default.yaml")
    n = normalize_all(cfg, ml_root)
    log.info("Done. %d arrays normalized.", n)
