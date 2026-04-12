# ChessMorph — Initial Project Scaffold

## Context
Greenfield ML application. The repo at `/Users/prathameshpatil/ChessMorph` is completely empty (only `.git`). The user wants two deliverables:
1. Recommended monorepo directory structure
2. Complete `ml/model.py` with `GameAssetVAE` class and `vae_loss()` function

## Spatial Dimension Analysis (model correctness)

Conv2d/ConvTranspose2d: kernel=4, stride=2, padding=1 throughout.

| Stage | Step | HxW in | Ch in | Ch out | HxW out |
|-------|------|---------|-------|--------|---------|
| Enc 1 | conv | 64×64   | 1     | 32     | 32×32   |
| Enc 2 | conv | 32×32   | 32    | 64     | 16×16   |
| Enc 3 | conv | 16×16   | 64    | 128    | 8×8     |
| Enc 4 | conv | 8×8     | 128   | 256    | 4×4     |
| Dec 1 | deconv | 4×4  | 256   | 128    | 8×8     |
| Dec 2 | deconv | 8×8  | 128   | 64     | 16×16   |
| Dec 3 | deconv | 16×16| 64    | 32     | 32×32   |
| Dec 4 | deconv | 32×32| 32    | 1      | 64×64   |

Flattened dim after encoder: `256 × 4 × 4 = 4096`
Linear layers: `fc_mu` and `fc_logvar`: `Linear(4096, 16)`
Decoder FC entry: `Linear(16, 4096)` → reshape to `(B, 256, 4, 4)`

## Directory Structure

```
ChessMorph/
├── ml/
│   ├── model.py          # GameAssetVAE + vae_loss  ← CREATE NOW
│   ├── train.py          # Training loop, saves full_vae.pt + decoder_only.pt
│   ├── dataset.py        # ChessPieceDataset (torch Dataset)
│   ├── transforms.py     # Resize to 64×64, normalize to [0,1], augmentations
│   ├── evaluate.py       # SSIM / FID metrics
│   └── export.py         # torch.jit.script(model.decoder) → TorchScript artifact
├── backend/
│   ├── main.py           # FastAPI app + lifespan + CORS
│   ├── router.py         # POST /generate endpoint
│   ├── decoder_wrapper.py# Loads decoder-only weights at startup (singleton)
│   ├── schemas.py        # Pydantic LatentVector / ImageResponse models
│   └── utils.py          # tensor ↔ base64 PNG conversion
├── frontend/
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── app/
│       │   ├── layout.tsx
│       │   └── page.tsx          # Main morph UI
│       ├── components/
│       │   ├── MorphSlider.tsx   # 16 latent-space sliders (-3 to 3, step 0.1)
│       │   └── PieceCanvas.tsx   # Renders returned base64 PNG
│       ├── lib/
│       │   └── api.ts            # Typed fetch wrapper with 100ms debounce
│       └── types/index.ts
├── docker/
│   ├── Dockerfile.ml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── data/
│   ├── raw/              # Original piece PNGs
│   └── processed/        # 64×64 grayscale preprocessed
├── checkpoints/
│   └── .gitkeep
├── notebooks/
│   └── exploration.ipynb
├── docker-compose.yml
├── requirements.txt
└── .gitignore
```

## Files to Create (Task 1 + 2)

### 1. `ml/model.py`
Full `GameAssetVAE` class containing:
- `Encoder` submodule (4× Conv2d blocks)
- `Decoder` submodule (4× ConvTranspose2d blocks)  
- `reparameterize()` — reparameterisation trick, returns `mu` at eval time
- `forward()` → returns `(x_hat, mu, logvar)`
- `_init_weights()` — Kaiming normal for Conv, Xavier uniform for Linear, BN identity
- `vae_loss()` standalone function with beta parameter

**Key design decisions:**
- MSE (not BCE) for reconstruction — chess sprites are anti-aliased continuous floats; BCE explodes near 0/1
- `beta=4.0` default — encourages disentangled morphing
- Final decoder layer: no BatchNorm (BN before Sigmoid degrades single-item batch inference), `bias=True`
- Encoder/decoder stored as named submodules so backend can filter state dict by prefix for decoder-only loading
- `__main__` sanity check validates all tensor shapes and prints parameter count

### 2. Supporting scaffold files
- `requirements.txt`
- `.gitignore`
- `checkpoints/.gitkeep`
- `data/raw/.gitkeep`, `data/processed/.gitkeep`

## Decoder-Only Inference Pattern (for future backend)

```python
# In backend/decoder_wrapper.py — no full VAE loaded
full_state = torch.load("checkpoints/full_vae.pt", map_location="cpu")
decoder = Decoder()
decoder.load_state_dict({
    k.removeprefix("decoder."): v
    for k, v in full_state.items()
    if k.startswith("decoder.")
})
```

## Verification

Run `python ml/model.py` — the `__main__` block:
1. Creates a `GameAssetVAE` and runs a batch of 4 dummy images through it
2. Asserts `x_hat.shape == (4, 1, 64, 64)`, `mu/logvar.shape == (4, 16)`
3. Computes `vae_loss` and prints all three loss components
4. Runs standalone `model.decode(z)` and asserts shape `(1, 1, 64, 64)`
5. Prints encoder/decoder/total parameter counts
