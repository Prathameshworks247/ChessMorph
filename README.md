# ChessMorph

**Live demo → [chess-morph-vae.vercel.app](https://chess-morph-vae.vercel.app)**

A Beta-VAE trained on chess piece silhouettes. Move 16 sliders to morph piece shapes continuously through a learned latent space — or interpolate between any two pieces to animate a smooth transition.

---

## Features

### Interactive Latent Space Explorer
- **16 sliders** (−3.0 → +3.0, step 0.1) each controlling one latent dimension
- **Real-time inference** — debounced 100 ms so every slider drag fires the decoder
- **Piece presets** — one-click snap to King, Queen, Rook, Bishop, Knight, or Pawn (♔ ♕ ♖ ♗ ♞ ♟)
- **Randomize** — sample a random Gaussian point in latent space
- **Reset** — zero all sliders to the neutral mean vector

### Morphing Animation
- **Save A / Save B** — store two latent vectors as keyframes
- **Animate** — linearly interpolates A → B → A over 12 frames at 80 ms/frame, creating a seamless looping morph
- Live frame counter while animating

### Visual Themes
Five CSS-filter themes for the generated 64 × 64 sprite:

| Theme | Look |
|-------|------|
| Classic | white / gray |
| Gold | sepia + warm saturation |
| Marble | pale stone |
| Neon | vivid green glow |
| Wood | amber grain |

---

## Model — Beta-VAE

### Architecture

**Encoder** (4 strided convolutions, 64 → 4 spatial):

| Layer | Channels | Output Size | Activation |
|-------|----------|-------------|------------|
| Conv2d k=4, s=2, p=1 | 1 → 32 | 32 × 32 | BN + LeakyReLU(0.2) |
| Conv2d k=4, s=2, p=1 | 32 → 64 | 16 × 16 | BN + LeakyReLU(0.2) |
| Conv2d k=4, s=2, p=1 | 64 → 128 | 8 × 8 | BN + LeakyReLU(0.2) |
| Conv2d k=4, s=2, p=1 | 128 → 256 | 4 × 4 | BN + LeakyReLU(0.2) |
| Flatten → fc_μ, fc_logvar | 4096 → 16 | — | — |

**Latent space:** 16-dimensional Gaussian (`z = μ + ε·σ`, reparameterisation trick)

**Decoder** (4 transposed convolutions, 4 → 64 spatial):

| Layer | Channels | Output Size | Activation |
|-------|----------|-------------|------------|
| Linear | 16 → 4096 | — | — |
| ConvTranspose2d k=4, s=2, p=1 | 256 → 128 | 8 × 8 | BN + ReLU |
| ConvTranspose2d k=4, s=2, p=1 | 128 → 64 | 16 × 16 | BN + ReLU |
| ConvTranspose2d k=4, s=2, p=1 | 64 → 32 | 32 × 32 | BN + ReLU |
| ConvTranspose2d k=4, s=2, p=1 | 32 → 1 | 64 × 64 | Sigmoid (no BN) |

No BatchNorm on the final decoder layer — prevents batch-norm divergence at batch size 1 during inference.

### Loss Function

```
L = MSE_recon + β · KL

MSE_recon = mean( (x̂ - x)² )
KL        = -0.5 · mean( 1 + logvar - μ² - exp(logvar) )
```

**MSE not BCE** — chess sprites are anti-aliased with continuous pixel values, not binary masks.

**β schedule** — β ramps linearly from 0 → 4.0 over epochs 5–25, then holds. Starting with β = 0 gives the encoder time to learn structure before KL pressure forces disentanglement.

### Training Hyperparameters

| Hyperparameter | Value |
|----------------|-------|
| Latent dim | 16 |
| Image size | 64 × 64 grayscale |
| Batch size | 64 |
| Max epochs | 100 |
| Learning rate | 1 × 10⁻³ (Adam) |
| LR scheduler | ReduceLROnPlateau (patience=5, factor=0.5) |
| β target | 4.0 |
| β warmup | 5 epochs at 0, then ramp over 20 epochs |
| Early stopping | patience=15 on validation reconstruction loss |
| Val split | 10 % |

### Dataset

- **Sources:** Lichess SVG piece sets, Wikimedia Cburnett set, selected OpenGameArt sets
- **Pipeline:** SVG → rasterise (64 × 64, alpha channel) → normalise (bbox crop, re-pad) → augment → pack HDF5
- **Augmentations (25× per piece):** rotation ±15°, affine scale/translate, elastic distortion, Gaussian blur
- **Final size:** ~9,000 64 × 64 greyscale images across 6 canonical piece types (King, Queen, Rook, Bishop, Knight, Pawn)
- **Storage:** single HDF5 file with gzip compression

### Inference

Only the **decoder** is exported — the encoder is not needed at runtime. The decoder is exported to ONNX (opset 17, dynamic batch) and served via ONNX Runtime, so the backend has no PyTorch dependency.

```
latent vector (16 floats) → ONNX decoder → (1, 1, 64, 64) → uint8 PNG → base64
```

---

## API

Backend: **FastAPI + ONNX Runtime**, hosted on Render.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Liveness check |
| GET | `/presets` | Pre-computed latent vectors for each piece type |
| POST | `/generate` | Decode a latent vector → base64 PNG |
| POST | `/interpolate` | Linear interpolation between two latent vectors → list of base64 PNGs |

**`POST /generate`**
```json
{ "latent": [0.1, -0.5, 1.2, ...] }   // 16 floats
```
```json
{ "image": "<base64 PNG>" }
```

**`POST /interpolate`**
```json
{ "latent_a": [...], "latent_b": [...], "steps": 12 }
```
```json
{ "images": ["<base64>", "<base64>", ...] }
```

---

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Backend | FastAPI, ONNX Runtime, Pillow |
| ML | PyTorch, Beta-VAE, Albumentations |
| Hosting | Vercel (frontend) + Render (backend) |

---

## Running Locally

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev          # http://localhost:3000
```

**Retrain from scratch**
```bash
cd ml
bash scripts/run_pipeline.sh   # build dataset
python src/train.py            # train VAE
python src/export.py           # export decoder → ONNX
python src/evaluate.py         # generate presets + eval visuals
```
