#!/usr/bin/env bash
# Run the full data pipeline: rasterize → normalize → pack
set -euo pipefail

# ARM64 cairo library needed for cairosvg
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:${DYLD_LIBRARY_PATH:-}"

ML_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ML_ROOT/src/data"

echo "=== Stage 1: Rasterize SVGs ==="
python3 "$SRC/rasterize.py"

echo "=== Stage 2: Normalize arrays ==="
python3 "$SRC/normalize.py"

echo "=== Stage 3: Augment + pack HDF5 ==="
python3 "$SRC/pack.py"

echo "=== Pipeline complete ==="
echo "Dataset: $ML_ROOT/data/chess_dataset.h5"
