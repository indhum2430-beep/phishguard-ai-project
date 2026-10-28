import time

from flask import Flask, jsonify, request
from flask_cors import CORS

from detector import _load, predict_url

app = Flask(__name__)
CORS(app)  # allow the Vite frontend to call this API

try:
    _load()  # load the model once at startup so the first scan is fast
except Exception:
    pass  # missing model files are reported when a scan is requested

# Status text sent to the React UI. Change these to match what ResultCard.jsx expects.
STATUS_SAFE = "SAFE"
STATUS_SUSPICIOUS = "SUSPICIOUS"
STATUS_PHISHING = "PHISHING"
SUSPICIOUS_FROM = 40   # phishing probability (%) at or above this = suspicious
PHISHING_FROM = 65     # phishing probability (%) at or above this = phishing


def get_url_from_request():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "")
    if not isinstance(url, str) or not url.strip():
        return None
    return url.strip()


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/predict")
def predict():
    url = get_url_from_request()
    if not url:
        return jsonify({"error": "Please provide a non-empty 'url' string"}), 400
    try:
        return jsonify(predict_url(url))
    except FileNotFoundError:
        return jsonify({"error": "Model files not found. Run train_model.py first."}), 500
    except Exception as exc:
        return jsonify({"error": f"Prediction failed: {exc}"}), 500


@app.post("/api/scan")
def scan():
    """Endpoint used by the React app (src/utils/analyzeURL.js)."""
    url = get_url_from_request()
    if not url:
        return jsonify({"error": "Please enter a URL."}), 400

    try:
        start = time.perf_counter()
        result = predict_url(url)
        latency_ms = round((time.perf_counter() - start) * 1000)
    except FileNotFoundError:
        return jsonify({"error": "Model files not found. Run train_model.py first."}), 500
    except Exception as exc:
        return jsonify({"error": f"Scan failed: {exc}"}), 500

    score = round(result["phishing_probability"] * 100)  # 0-100 risk score
    if score >= PHISHING_FROM:
        status = STATUS_PHISHING
    elif score >= SUSPICIOUS_FROM:
        status = STATUS_SUSPICIOUS
    else:
        status = STATUS_SAFE

    if result.get("trusted"):
        reasons = result["reasons"]
    else:
        reasons = [f"Machine-learning model estimates a {score}% chance this site is phishing."]
        reasons += result["reasons"]

    return jsonify({
        "url": url,
        "score": score,
        "status": status,
        "label": result["label"],
        "is_phishing": result["is_phishing"],
        "confidence": None if result.get("trusted") else round(result["confidence"] * 100),
        "latency": latency_ms,
        "reasons": reasons,
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)