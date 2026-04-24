from __future__ import annotations

import base64
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Patch the ONNX session so tests don't need the actual model file
sys.path.insert(0, str(Path(__file__).parents[1]))


def make_client():
    import numpy as np

    mock_session = MagicMock()
    # Return a (1,1,64,64) float32 array
    mock_session.run.return_value = [np.zeros((1, 1, 64, 64), dtype=np.float32)]

    with patch("app.inference.load_session", return_value=mock_session), \
         patch("app.config.settings.MODEL_PATH", Path("/fake/decoder.onnx")), \
         patch("pathlib.Path.exists", return_value=True):
        from app.main import app
        return TestClient(app, raise_server_exceptions=True)


@pytest.fixture(scope="module")
def client():
    return make_client()


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_generate_valid(client):
    resp = client.post("/generate", json={"latent": [0.0] * 16})
    assert resp.status_code == 200
    data = resp.json()
    assert "image" in data
    # Verify it's valid base64
    decoded = base64.b64decode(data["image"])
    assert len(decoded) > 0


def test_generate_wrong_length(client):
    resp = client.post("/generate", json={"latent": [0.0] * 10})
    assert resp.status_code == 422


def test_generate_non_numeric(client):
    resp = client.post("/generate", json={"latent": ["a"] * 16})
    assert resp.status_code == 422
