from __future__ import annotations

import logging
from pathlib import Path

import albumentations as A
import numpy as np
import yaml

log = logging.getLogger(__name__)


def load_config(config_path: Path) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def build_pipeline(cfg: dict) -> A.Compose:
    aug = cfg["augmentation"]
    return A.Compose([
        A.Rotate(limit=aug["rotate_limit"], p=aug["rotate_p"], border_mode=0),
        A.Affine(
            scale=(aug["affine_scale_min"], aug["affine_scale_max"]),
            translate_px=(-aug["affine_translate_px"], aug["affine_translate_px"]),
            p=aug["affine_p"],
        ),
        A.ElasticTransform(
            alpha=aug["elastic_alpha"],
            sigma=aug["elastic_sigma"],
            p=aug["elastic_p"],
        ),
        A.GaussianBlur(
            blur_limit=(1, aug["blur_limit"]),
            p=aug["blur_p"],
        ),
    ])


def augment_array(
    alpha: np.ndarray,
    pipeline: A.Compose,
    n_copies: int,
) -> list[np.ndarray]:
    """Return `n_copies` augmented versions of `alpha`."""
    uint8 = (alpha * 255).astype(np.uint8)
    results: list[np.ndarray] = []
    for _ in range(n_copies):
        out = pipeline(image=uint8)["image"]
        results.append(out.astype(np.float32) / 255.0)
    return results


def augment_all(cfg: dict, ml_root: Path) -> list[tuple[np.ndarray, str, str]]:
    """Return list of (array, set_name, piece_type) tuples for all augmented images."""
    rendered_root = ml_root / cfg["paths"]["rendered"]
    n_copies = cfg["data"]["augmentation_factor"]
    piece_map: dict[str, str] = cfg["data"]["piece_map"]
    pipeline = build_pipeline(cfg)

    records: list[tuple[np.ndarray, str, str]] = []
    for set_dir in sorted(rendered_root.iterdir()):
        if not set_dir.is_dir():
            continue
        set_name = set_dir.name
        for npy_file in sorted(set_dir.glob("*.npy")):
            stem = npy_file.stem
            piece_type = piece_map.get(stem, "unknown")
            alpha = np.load(npy_file)
            augmented = augment_array(alpha, pipeline, n_copies)
            for arr in augmented:
                records.append((arr, set_name, piece_type))
        log.info("Augmented set %s (%d records so far)", set_name, len(records))

    log.info("Total augmented records: %d", len(records))
    return records


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ml_root = Path(__file__).resolve().parents[2]
    cfg = load_config(ml_root / "configs" / "default.yaml")
    records = augment_all(cfg, ml_root)
    log.info("Done. %d total augmented images.", len(records))
