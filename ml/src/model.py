from __future__ import annotations

import logging

import torch
import torch.nn as nn
from torch import Tensor

log = logging.getLogger(__name__)

LATENT_DIM = 16
ENCODER_CHANNELS = [1, 32, 64, 128, 256]
DECODER_CHANNELS = [256, 128, 64, 32, 1]
BOTTLENECK = 256 * 4 * 4  # 4096


class GameAssetVAE(nn.Module):
    def __init__(self, latent_dim: int = LATENT_DIM) -> None:
        super().__init__()
        self.latent_dim = latent_dim

        # Encoder: 64 → 32 → 16 → 8 → 4
        self.encoder = nn.Sequential(
            *[
                nn.Sequential(
                    nn.Conv2d(ENCODER_CHANNELS[i], ENCODER_CHANNELS[i + 1],
                              kernel_size=4, stride=2, padding=1),
                    nn.BatchNorm2d(ENCODER_CHANNELS[i + 1]),
                    nn.LeakyReLU(0.2, inplace=True),
                )
                for i in range(len(ENCODER_CHANNELS) - 1)
            ]
        )

        self.fc_mu = nn.Linear(BOTTLENECK, latent_dim)
        self.fc_logvar = nn.Linear(BOTTLENECK, latent_dim)

        self.fc_decode = nn.Linear(latent_dim, BOTTLENECK)

        # Decoder: 4 → 8 → 16 → 32 → 64
        decoder_blocks: list[nn.Module] = []
        for i in range(len(DECODER_CHANNELS) - 1):
            is_last = (i == len(DECODER_CHANNELS) - 2)
            decoder_blocks.append(nn.Sequential(
                nn.ConvTranspose2d(
                    DECODER_CHANNELS[i], DECODER_CHANNELS[i + 1],
                    kernel_size=4, stride=2, padding=1,
                ),
                nn.BatchNorm2d(DECODER_CHANNELS[i + 1]) if not is_last else nn.Identity(),
                nn.ReLU(inplace=True) if not is_last else nn.Sigmoid(),
            ))
        self.decoder = nn.Sequential(*decoder_blocks)

    def encode(self, x: Tensor) -> tuple[Tensor, Tensor]:
        h = self.encoder(x)
        h = h.flatten(1)
        return self.fc_mu(h), self.fc_logvar(h)

    def reparameterize(self, mu: Tensor, logvar: Tensor) -> Tensor:
        if self.training:
            std = torch.exp(0.5 * logvar)
            eps = torch.randn_like(std)
            return mu + eps * std
        return mu

    def decode(self, z: Tensor) -> Tensor:
        h = self.fc_decode(z)
        h = h.view(-1, 256, 4, 4)
        return self.decoder(h)

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        recon = self.decode(z)
        return recon, mu, logvar


def vae_loss(
    recon: Tensor,
    x: Tensor,
    mu: Tensor,
    logvar: Tensor,
    beta: float = 4.0,
) -> dict[str, Tensor]:
    batch_size = x.size(0)
    recon_loss = nn.functional.binary_cross_entropy(recon, x, reduction="sum") / batch_size
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp()) / batch_size
    total = recon_loss + beta * kl_loss
    return {"total": total, "recon": recon_loss, "kl": kl_loss}
