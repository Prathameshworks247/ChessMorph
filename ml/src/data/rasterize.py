from __future__ import annotations

import logging
from pathlib import Path

import cairosvg
import numpy as np
from PIL import Image
import io
import yaml

log = logging.getLogger(__name__)


def load_config(config_path: Path) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def rasterize_svg(svg_path: Path, size: int = 64) -> np.ndarray | None:
    """Render SVG → RGBA at `size`×`size`, return alpha channel as float32 [0,1]."""
    try:
        png_bytes = cairosvg.svg2png(
            url=str(svg_path),
            output_width=size,
            output_height=size,
        )
        img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        alpha = np.array(img)[:, :, 3].astype(np.float32) / 255.0
        return alpha
    except Exception as exc:
        log.warning("Failed to rasterize %s: %s", svg_path, exc)
        return None


def rasterize_all(cfg: dict, ml_root: Path) -> int:
    src_dir = Path(cfg["paths"]["source_svgs"])
    if not src_dir.is_absolute():
        src_dir = ml_root / src_dir

    out_root = ml_root / cfg["paths"]["rendered"]
    out_root.mkdir(parents=True, exist_ok=True)

    size = cfg["data"]["image_size"]
    piece_map: dict[str, str] = cfg["data"]["piece_map"]

    count = 0
    for set_dir in sorted(src_dir.iterdir()):
        if not set_dir.is_dir():
            continue
        set_name = set_dir.name
        set_out = out_root / set_name
        set_out.mkdir(exist_ok=True)

        for svg_file in sorted(set_dir.glob("*.svg")):
            stem = svg_file.stem           # e.g. "wK"
            piece_type = piece_map.get(stem)
            if piece_type is None:
                log.warning("Unknown piece stem %s in %s, skipping", stem, set_name)
                continue

            out_path = set_out / f"{stem}.npy"
            if out_path.exists():
                count += 1
                continue

            alpha = rasterize_svg(svg_file, size)
            if alpha is None:
                continue

            np.save(out_path, alpha)
            count += 1
            log.debug("Saved %s", out_path)

        log.info("Rasterized set %s", set_name)

    log.info("Total rasterized: %d", count)
    return count


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ml_root = Path(__file__).resolve().parents[2]
    cfg = load_config(ml_root / "configs" / "default.yaml")
    n = rasterize_all(cfg, ml_root)
    log.info("Done. %d arrays saved.", n)
