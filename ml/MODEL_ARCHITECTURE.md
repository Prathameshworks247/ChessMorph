# GameAssetVAE — Model Architecture

---

## Overview

```
Input (B, 1, 64, 64)
        │
        ▼
┌───────────────┐
│    ENCODER    │
│  4× Conv2d    │
│  BN + LReLU   │
└───────┬───────┘
        │  (B, 4096)
        ├──────────────┐
        ▼              ▼
   fc_mu (Linear)  fc_logvar (Linear)
   (B, 16)         (B, 16)
        │              │
        └──────┬────────┘
               ▼
     Reparameterize: z = μ + ε·σ
               │  (B, 16)
               ▼
┌───────────────────────┐
│       DECODER         │
│  Linear → reshape     │
│  4× ConvTranspose2d   │
│  BN + ReLU → Sigmoid  │
└───────────┬───────────┘
            ▼
    Output (B, 1, 64, 64)
```

---

## Encoder

| Layer | Op | In → Out channels | Spatial | Activation |
|-------|----|-------------------|---------|------------|
| conv1 | Conv2d k=4, s=2, p=1 | 1 → 32 | 64×64 → 32×32 | BatchNorm + LeakyReLU(0.2) |
| conv2 | Conv2d k=4, s=2, p=1 | 32 → 64 | 32×32 → 16×16 | BatchNorm + LeakyReLU(0.2) |
| conv3 | Conv2d k=4, s=2, p=1 | 64 → 128 | 16×16 → 8×8 | BatchNorm + LeakyReLU(0.2) |
| conv4 | Conv2d k=4, s=2, p=1 | 128 → 256 | 8×8 → 4×4 | BatchNorm + LeakyReLU(0.2) |
| flatten | — | 256×4×4 → **4096** | — | — |
| fc_mu | Linear | 4096 → **16** | — | — |
| fc_logvar | Linear | 4096 → **16** | — | — |

---

## Latent Space

```
std    = exp(0.5 × logvar)
ε      ~ N(0, I)
z      = μ + ε × std        ← training
z      = μ                  ← eval (deterministic)
```

Dimension: **16**  |  Prior: **N(0, I)**

---

## Decoder

| Layer | Op | In → Out channels | Spatial | Activation |
|-------|----|-------------------|---------|------------|
| fc | Linear | 16 → 4096 | — | — |
| reshape | — | 4096 → 256×4×4 | — | — |
| deconv1 | ConvTranspose2d k=4, s=2, p=1 | 256 → 128 | 4×4 → 8×8 | BatchNorm + ReLU |
| deconv2 | ConvTranspose2d k=4, s=2, p=1 | 128 → 64 | 8×8 → 16×16 | BatchNorm + ReLU |
| deconv3 | ConvTranspose2d k=4, s=2, p=1 | 64 → 32 | 16×16 → 32×32 | BatchNorm + ReLU |
| deconv4 | ConvTranspose2d k=4, s=2, p=1 | 32 → 1 | 32×32 → 64×64 | **Sigmoid** (no BN) |

> **Why no BatchNorm on the final layer:** BN before Sigmoid shifts the distribution and breaks batch-size-1 inference at serve time (the backend decodes one vector at a time).

---

## Loss Function — Beta-VAE

```
L = MSE(x̂, x)  +  β · KL(q(z|x) ∥ N(0,I))

KL = -0.5 · Σⱼ ( 1 + logvar_j − μ_j² − exp(logvar_j) )
```

| Term | Choice | Reason |
|------|--------|--------|
| Reconstruction | **MSE** | Sprites are anti-aliased — pixel values are continuous floats. BCE explodes near 0/1 on smooth edges. |
| KL weight β | **4.0** (default) | β > 1 encourages disentangled latent dims, enabling smooth slider-based morphing. Range: 1–10. |
| KL reduction | mean over batch | Keeps β interpretable regardless of batch size. |

---

## Weight Initialisation

| Module type | Init |
|-------------|------|
| Conv2d / ConvTranspose2d | Kaiming normal (`fan_out`, `leaky_relu`) |
| BatchNorm2d | weight = 1, bias = 0 |
| Linear | Xavier uniform |

---

## Parameter Count (approximate)

| Component | Params |
|-----------|--------|
| Encoder conv stack | ~1.5 M |
| Encoder FC heads (×2) | ~131 K |
| Decoder FC | ~66 K |
| Decoder deconv stack | ~1.5 M |
| **Total** | **~3.2 M** |
