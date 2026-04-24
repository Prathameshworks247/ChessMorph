from __future__ import annotations

import base64
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))


@pytest.fixture(scope="module")
def client():
    mock_session = MagicMock()
    mock_session.run.return_value = [np.zeros((1, 1, 64, 64), dtype=np.float32)]

    with patch("app.inference.load_session", return_value=mock_session), \
         patch.object(Path, "exists", return_value=True):
        from app.main import app
        from fastapi.testclient import TestClient

        with TestClient(app) as c:
            # Inject session directly in case lifespan skips due to missing file
            app.state.session = mock_session
            yield c


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_generate_valid(client):
    resp = client.post("/generate", json={"latent": [0.0] * 16})
    assert resp.status_code == 200
    data = resp.json()
    assert "image" in data
    decoded = base64.b64decode(data["image"])
    assert len(decoded) > 0


def test_generate_wrong_length(client):
    resp = client.post("/generate", json={"latent": [0.0] * 10})
    assert resp.status_code == 422


def test_generate_non_numeric(client):
    resp = client.post("/generate", json={"latent": ["a"] * 16})
    assert resp.status_code == 422
