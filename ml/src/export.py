from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import torch
import yaml

sys.path.insert(0, str(Path(__file__).parent))
from model import GameAssetVAE

log = logging.getLogger(__name__)


def load_config(config_path: Path) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


class DecoderOnly(torch.nn.Module):
    """Wraps just the decoder for ONNX export."""

    def __init__(self, vae: GameAssetVAE) -> None:
        super().__init__()
        self.fc_decode = vae.fc_decode
        self.decoder = vae.decoder

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        h = self.fc_decode(z)
        h = h.view(-1, 256, 4, 4)
        return self.decoder(h)


def export_decoder(cfg: dict, ml_root: Path) -> Path:
    import onnx
    import onnxruntime as ort

    latent_dim = cfg["data"]["latent_dim"]
    ckpt_path = ml_root / cfg["paths"]["checkpoints"] / "best.pt"
    out_path = ml_root / cfg["paths"]["exports"] / "decoder.onnx"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    device = torch.device("cpu")
    vae = GameAssetVAE(latent_dim=latent_dim)
    ckpt = torch.load(ckpt_path, map_location=device)
    vae.load_state_dict(ckpt["model_state"])
    vae.eval()

    decoder = DecoderOnly(vae)
    decoder.eval()

    dummy = torch.zeros(1, latent_dim)
    torch.onnx.export(
        decoder,
        dummy,
        str(out_path),
        input_names=["latent_vector"],
        output_names=["generated_image"],
        dynamic_axes={"latent_vector": {0: "batch"}, "generated_image": {0: "batch"}},
        opset_version=17,
        do_constant_folding=True,
    )
    log.info("Exported ONNX to %s", out_path)

    # Verify ONNX matches PyTorch
    onnx.checker.check_model(str(out_path))
    sess = ort.InferenceSession(str(out_path))
    z_np = dummy.numpy()
    ort_out = sess.run(["generated_image"], {"latent_vector": z_np})[0]

    with torch.no_grad():
        pt_out = decoder(dummy).numpy()

    max_diff = np.abs(ort_out - pt_out).max()
    log.info("Max difference ONNX vs PyTorch: %.2e", max_diff)
    assert max_diff < 1e-4, f"ONNX/PyTorch mismatch: {max_diff}"

    size_mb = out_path.stat().st_size / 1024 / 1024
    log.info("ONNX file size: %.2f MB", size_mb)
    assert size_mb < 10, f"ONNX file too large: {size_mb:.2f} MB"

    log.info("Export verified OK")
    return out_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ml_root = Path(__file__).resolve().parents[1]
    cfg = load_config(ml_root / "configs" / "default.yaml")
    out = export_decoder(cfg, ml_root)
    log.info("Done. ONNX at %s", out)
