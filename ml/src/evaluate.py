from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import torch
import yaml

sys.path.insert(0, str(Path(__file__).parent))
from model import GameAssetVAE
from data.dataset import ChessDataset

log = logging.getLogger(__name__)


def load_config(config_path: Path) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_model(cfg: dict, ml_root: Path, device: torch.device) -> GameAssetVAE:
    ckpt_path = ml_root / cfg["paths"]["checkpoints"] / "best.pt"
    model = GameAssetVAE(latent_dim=cfg["data"]["latent_dim"]).to(device)
    ckpt = torch.load(ckpt_path, map_location=device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    log.info("Loaded checkpoint from %s", ckpt_path)
    return model


def reconstruction_grid(
    model: GameAssetVAE,
    dataset: ChessDataset,
    n: int = 32,
    device: torch.device = torch.device("cpu"),
    save_path: Path | None = None,
) -> None:
    """Save a grid of real vs reconstructed images."""
    import matplotlib.pyplot as plt

    indices = np.random.choice(len(dataset), n, replace=False)
    imgs = torch.stack([dataset[int(i)] for i in indices]).to(device)

    with torch.no_grad():
        recon, _, _ = model(imgs)

    fig, axes = plt.subplots(2, n, figsize=(n, 4))
    for j in range(n):
        axes[0, j].imshow(imgs[j, 0].cpu().numpy(), cmap="gray", vmin=0, vmax=1)
        axes[0, j].axis("off")
        axes[1, j].imshow(recon[j, 0].cpu().numpy(), cmap="gray", vmin=0, vmax=1)
        axes[1, j].axis("off")

    axes[0, 0].set_ylabel("Real", rotation=90, fontsize=8)
    axes[1, 0].set_ylabel("Recon", rotation=90, fontsize=8)
    plt.tight_layout()

    out = save_path or Path("reconstruction_grid.png")
    plt.savefig(out, dpi=100, bbox_inches="tight")
    plt.close()
    log.info("Saved reconstruction grid to %s", out)


def latent_traversal(
    model: GameAssetVAE,
    latent_dim: int = 16,
    n_steps: int = 9,
    z_range: float = 3.0,
    device: torch.device = torch.device("cpu"),
    save_path: Path | None = None,
) -> None:
    """For each latent dim, vary it from -z_range to +z_range while others stay 0."""
    import matplotlib.pyplot as plt

    z_base = torch.zeros(1, latent_dim, device=device)
    steps = torch.linspace(-z_range, z_range, n_steps)

    fig, axes = plt.subplots(latent_dim, n_steps, figsize=(n_steps * 1.2, latent_dim * 1.2))

    with torch.no_grad():
        for dim in range(latent_dim):
            for j, val in enumerate(steps):
                z = z_base.clone()
                z[0, dim] = val
                img = model.decode(z)[0, 0].cpu().numpy()
                axes[dim, j].imshow(img, cmap="gray", vmin=0, vmax=1)
                axes[dim, j].axis("off")
            axes[dim, 0].set_ylabel(f"Dim {dim + 1}", fontsize=7, rotation=90)

    plt.suptitle("Latent traversal (−3 → +3)", fontsize=10)
    plt.tight_layout()
    out = save_path or Path("latent_traversal.png")
    plt.savefig(out, dpi=100, bbox_inches="tight")
    plt.close()
    log.info("Saved latent traversal to %s", out)


def compute_pca(
    model: GameAssetVAE,
    dataset: ChessDataset,
    n_components: int = 16,
    device: torch.device = torch.device("cpu"),
    save_path: Path | None = None,
) -> np.ndarray:
    """Encode full dataset, fit PCA, save principal components."""
    from sklearn.decomposition import PCA
    from torch.utils.data import DataLoader

    loader = DataLoader(dataset, batch_size=256, shuffle=False, num_workers=0)
    mus: list[np.ndarray] = []

    with torch.no_grad():
        for batch in loader:
            mu, _ = model.encode(batch.to(device))
            mus.append(mu.cpu().numpy())

    all_mus = np.concatenate(mus, axis=0)
    pca = PCA(n_components=n_components)
    pca.fit(all_mus)

    out = save_path or Path("pca_components.npy")
    np.save(out, {
        "components": pca.components_,
        "mean": pca.mean_,
        "explained_variance_ratio": pca.explained_variance_ratio_,
    })
    log.info("Explained variance: %s", np.round(pca.explained_variance_ratio_, 3))
    log.info("Saved PCA components to %s", out)
    return pca.components_


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ml_root = Path(__file__).resolve().parents[1]
    cfg = load_config(ml_root / "configs" / "default.yaml")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = load_model(cfg, ml_root, device)
    dataset = ChessDataset(ml_root / cfg["paths"]["dataset"])
    out_dir = ml_root / "exports"
    out_dir.mkdir(exist_ok=True)

    reconstruction_grid(model, dataset, device=device, save_path=out_dir / "reconstruction_grid.png")
    latent_traversal(model, cfg["data"]["latent_dim"], device=device, save_path=out_dir / "latent_traversal.png")
    compute_pca(model, dataset, cfg["data"]["latent_dim"], device=device, save_path=out_dir / "pca_components.npy")
