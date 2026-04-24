from __future__ import annotations

import logging
from pathlib import Path

import h5py
import numpy as np
import yaml

log = logging.getLogger(__name__)


def load_config(config_path: Path) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def pack(
    records: list[tuple[np.ndarray, str, str]],
    out_path: Path,
    compression_level: int = 4,
) -> None:
    """Write records to HDF5.

    Args:
        records: list of (array (64,64), source_set, piece_type)
        out_path: destination .h5 file
        compression_level: gzip level
    """
    n = len(records)
    size = records[0][0].shape[0]

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(out_path, "w") as f:
        images_ds = f.create_dataset(
            "images",
            shape=(n, 1, size, size),
            dtype=np.float32,
            compression="gzip",
            compression_opts=compression_level,
            chunks=(64, 1, size, size),
        )
        dt = h5py.special_dtype(vlen=str)
        source_ds = f.create_dataset("source_set", shape=(n,), dtype=dt)
        piece_ds = f.create_dataset("piece_type", shape=(n,), dtype=dt)

        for i, (arr, src, piece) in enumerate(records):
            images_ds[i, 0] = arr
            source_ds[i] = src
            piece_ds[i] = piece

            if (i + 1) % 1000 == 0:
                log.info("Packed %d / %d", i + 1, n)

    log.info("Saved HDF5 to %s  (shape: %d, 1, %d, %d)", out_path, n, size, size)


def run_pack(cfg: dict, ml_root: Path) -> Path:
    from augment import augment_all  # noqa: PLC0415

    records = augment_all(cfg, ml_root)
    out_path = ml_root / cfg["paths"]["dataset"]
    compression = cfg["data"]["hdf5_compression"]
    pack(records, out_path, compression)
    return out_path


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ml_root = Path(__file__).resolve().parents[2]
    cfg = load_config(ml_root / "configs" / "default.yaml")
    out = run_pack(cfg, ml_root)
    log.info("Done. Dataset at %s", out)
