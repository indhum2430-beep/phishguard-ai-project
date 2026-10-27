import pytest

import app as app_module


def fake_result(probability=0.9, trusted=False):
    return {
        "url": "http://example.com",
        "is_phishing": probability >= 0.5,
        "label": "phishing" if probability >= 0.5 else "legitimate",
        "confidence": max(probability, 1 - probability),
        "phishing_probability": probability,
        "reasons": ["Fake finding."],
        **({"trusted": True} if trusted else {}),
    }


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


@pytest.fixture
def mock_model(monkeypatch):
    """Replace the real model with a fake so API tests do not need model files."""
    def _set(result=None, error=None):
        def fake_predict(url):
            if error:
                raise error
            return result
        monkeypatch.setattr(app_module, "predict_url", fake_predict)
    return _set


# ---------- /health ----------

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


# ---------- /api/scan: input validation ----------

@pytest.mark.parametrize("body", [{}, {"url": ""}, {"url": "   "}, {"url": 123}, {"url": None}])
def test_scan_rejects_bad_input(client, body):
    r = client.post("/api/scan", json=body)
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_scan_rejects_invalid_json(client):
    r = client.post("/api/scan", data="not json", content_type="application/json")
    assert r.status_code == 400


# ---------- /api/scan: results ----------

def test_scan_phishing_result(client, mock_model):
    mock_model(fake_result(0.9))
    data = client.post("/api/scan", json={"url": "http://example.com"}).get_json()

    assert data["score"] == 90
    assert data["status"] == app_module.STATUS_PHISHING
    assert data["is_phishing"] is True
    assert data["confidence"] == 90
    assert isinstance(data["latency"], int)
    assert data["reasons"][0].startswith("Machine-learning model estimates a 90%")
    assert "Fake finding." in data["reasons"]


@pytest.mark.parametrize(
    "probability, expected",
    [
        (0.10, app_module.STATUS_SAFE),
        (0.39, app_module.STATUS_SAFE),
        (0.40, app_module.STATUS_SUSPICIOUS),
        (0.64, app_module.STATUS_SUSPICIOUS),
        (0.65, app_module.STATUS_PHISHING),
        (0.99, app_module.STATUS_PHISHING),
    ],
)
def test_scan_status_thresholds(client, mock_model, probability, expected):
    mock_model(fake_result(probability))
    data = client.post("/api/scan", json={"url": "http://example.com"}).get_json()
    assert data["status"] == expected


def test_scan_trusted_site(client, mock_model):
    mock_model(fake_result(0.0, trusted=True))
    data = client.post("/api/scan", json={"url": "http://110.172.151.102"}).get_json()

    assert data["score"] == 0
    assert data["status"] == app_module.STATUS_SAFE
    assert data["confidence"] is None
    assert not any("Machine-learning" in r for r in data["reasons"])


# ---------- /api/scan: failures ----------

def test_scan_missing_model_files_gives_500(client, mock_model):
    mock_model(error=FileNotFoundError())
    r = client.post("/api/scan", json={"url": "http://example.com"})
    assert r.status_code == 500
    assert "Model files not found" in r.get_json()["error"]


def test_scan_unexpected_error_gives_500(client, mock_model):
    mock_model(error=RuntimeError("boom"))
    r = client.post("/api/scan", json={"url": "http://example.com"})
    assert r.status_code == 500
    assert "Scan failed" in r.get_json()["error"]


# ---------- /predict ----------

def test_predict_returns_model_result(client, mock_model):
    mock_model(fake_result(0.2))
    r = client.post("/predict", json={"url": "http://example.com"})
    assert r.status_code == 200
    assert r.get_json()["label"] == "legitimate"


def test_predict_rejects_empty_url(client):
    r = client.post("/predict", json={"url": ""})
    assert r.status_code == 400