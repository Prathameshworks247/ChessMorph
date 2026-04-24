from __future__ import annotations

import logging
from pathlib import Path

import h5py
import numpy as np
import torch
from torch.utils.data import Dataset

log = logging.getLogger(__name__)


class ChessDataset(Dataset):
    """Lazy-loading HDF5 dataset returning (1, 64, 64) float32 tensors."""

    def __init__(self, h5_path: str | Path) -> None:
        self.h5_path = Path(h5_path)
        # Open once to get length, then close — workers reopen lazily
        with h5py.File(self.h5_path, "r") as f:
            self._len = len(f["images"])
        self._file: h5py.File | None = None

    def _open(self) -> None:
        if self._file is None:
            self._file = h5py.File(self.h5_path, "r")

    def __len__(self) -> int:
        return self._len

    def __getitem__(self, idx: int) -> torch.Tensor:
        self._open()
        arr = self._file["images"][idx]          # (1, 64, 64) float32
        return torch.from_numpy(np.array(arr, dtype=np.float32))

    def __del__(self) -> None:
        if self._file is not None:
            try:
                self._file.close()
            except Exception:
                pass
