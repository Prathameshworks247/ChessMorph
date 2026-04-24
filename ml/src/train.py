from __future__ import annotations

import logging
import sys
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
import yaml

sys.path.insert(0, str(Path(__file__).parent))
from model import GameAssetVAE, vae_loss
from data.dataset import ChessDataset

log = logging.getLogger(__name__)


def load_config(config_path: Path) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def beta_schedule(epoch: int, warmup: int, ramp: int, beta_target: float) -> float:
    if epoch < warmup:
        return 0.0
    if epoch < warmup + ramp:
        return beta_target * (epoch - warmup) / ramp
    return beta_target


def save_checkpoint(model: GameAssetVAE, path: Path, meta: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model_state": model.state_dict(), **meta}, path)
    log.info("Saved checkpoint %s", path)


def train(config_path: Path | None = None) -> None:
    ml_root = Path(__file__).resolve().parents[1]
    if config_path is None:
        config_path = ml_root / "configs" / "default.yaml"
    cfg = load_config(config_path)

    tc = cfg["training"]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info("Device: %s", device)

    # W&B (optional — fallback to console logging)
    use_wandb = False
    try:
        import wandb
        wandb.init(project=tc["wandb_project"], config=cfg)
        use_wandb = True
    except Exception as exc:
        log.warning("W&B unavailable (%s), logging to console only", exc)

    # Dataset
    h5_path = ml_root / cfg["paths"]["dataset"]
    full_ds = ChessDataset(h5_path)
    val_size = int(len(full_ds) * tc["val_split"])
    train_size = len(full_ds) - val_size
    train_ds, val_ds = random_split(
        full_ds, [train_size, val_size],
        generator=torch.Generator().manual_seed(42),
    )
    train_loader = DataLoader(
        train_ds, batch_size=tc["batch_size"], shuffle=True,
        num_workers=tc["num_workers"], pin_memory=device.type == "cuda",
    )
    val_loader = DataLoader(
        val_ds, batch_size=tc["batch_size"], shuffle=False,
        num_workers=tc["num_workers"],
    )
    log.info("Train: %d  Val: %d", train_size, val_size)

    # Model
    model = GameAssetVAE(latent_dim=cfg["data"]["latent_dim"]).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=tc["lr"])
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, patience=tc["scheduler_patience"], factor=0.5, verbose=True,
    )

    ckpt_dir = ml_root / cfg["paths"]["checkpoints"]
    best_val = float("inf")
    epochs_no_improve = 0

    for epoch in range(1, tc["epochs"] + 1):
        beta = beta_schedule(
            epoch - 1,
            tc["beta_warmup_epochs"],
            tc["beta_ramp_epochs"],
            tc["beta_target"],
        )

        # --- train ---
        model.train()
        train_totals = {"total": 0.0, "recon": 0.0, "kl": 0.0}
        for batch in train_loader:
            x = batch.to(device)
            recon, mu, logvar = model(x)
            losses = vae_loss(recon, x, mu, logvar, beta=beta)
            optimizer.zero_grad()
            losses["total"].backward()
            optimizer.step()
            for k in train_totals:
                train_totals[k] += losses[k].item()

        n_batches = len(train_loader)
        train_avg = {k: v / n_batches for k, v in train_totals.items()}

        # --- val ---
        model.eval()
        val_totals = {"total": 0.0, "recon": 0.0, "kl": 0.0}
        recon_images: list[tuple] = []
        with torch.no_grad():
            for batch in val_loader:
                x = batch.to(device)
                recon, mu, logvar = model(x)
                losses = vae_loss(recon, x, mu, logvar, beta=beta)
                for k in val_totals:
                    val_totals[k] += losses[k].item()
                if len(recon_images) == 0:
                    recon_images = [(x[:8].cpu(), recon[:8].cpu())]

        n_val = len(val_loader)
        val_avg = {k: v / n_val for k, v in val_totals.items()}

        log.info(
            "Epoch %3d | β=%.2f | train total=%.2f recon=%.2f kl=%.4f | "
            "val total=%.2f recon=%.2f kl=%.4f",
            epoch, beta,
            train_avg["total"], train_avg["recon"], train_avg["kl"],
            val_avg["total"], val_avg["recon"], val_avg["kl"],
        )

        if use_wandb:
            import wandb
            log_dict = {
                "epoch": epoch,
                "beta": beta,
                "train/total": train_avg["total"],
                "train/recon": train_avg["recon"],
                "train/kl": train_avg["kl"],
                "val/total": val_avg["total"],
                "val/recon": val_avg["recon"],
                "val/kl": val_avg["kl"],
            }
            if epoch % tc["log_image_every_n_epochs"] == 0 and recon_images:
                inp, out = recon_images[0]
                pairs = torch.cat([inp, out], dim=0)
                log_dict["reconstructions"] = [
                    wandb.Image(pairs[i, 0].numpy(), caption=f"{'input' if i < 8 else 'recon'}")
                    for i in range(min(16, pairs.size(0)))
                ]
            wandb.log(log_dict)

        scheduler.step(val_avg["total"])

        # Checkpoints
        if epoch % tc["save_checkpoint_every_n_epochs"] == 0:
            save_checkpoint(model, ckpt_dir / f"epoch_{epoch}.pt", {"epoch": epoch})

        if val_avg["total"] < best_val:
            best_val = val_avg["total"]
            epochs_no_improve = 0
            save_checkpoint(model, ckpt_dir / "best.pt", {"epoch": epoch, "val_loss": best_val})
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= tc["early_stopping_patience"]:
                log.info("Early stopping at epoch %d", epoch)
                break

    if use_wandb:
        import wandb
        wandb.finish()
    log.info("Training complete. Best val loss: %.4f", best_val)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    train()
