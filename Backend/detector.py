"""Feature extraction and prediction for phishing URL detection."""

import math
import re
from pathlib import Path
from urllib.parse import urlparse

import joblib
import pandas as pd

BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "phishing_model.pkl"
FEATURES_PATH = BASE_DIR / "feature_names.pkl"

SUSPICIOUS_WORDS = (
    "login", "signin", "verify", "update", "secure", "account", "bank",
    "confirm", "password", "paypal", "wallet", "billing", "support", "free",
)
SHORTENERS = ("bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "buff.ly", "cutt.ly")
SUSPICIOUS_TLDS = (".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".click", ".zip")
IP_PATTERN = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")


def _entropy(text):
    if not text:
        return 0.0
    freq = {c: text.count(c) for c in set(text)}
    return -sum((n / len(text)) * math.log2(n / len(text)) for n in freq.values())


def extract_features(url):
    """Turn a raw URL string into a dict of numeric features."""
    url = (url or "").strip()
    uses_https = int(url.lower().startswith("https://"))
    parsed = urlparse(url if "://" in url else "http://" + url)

    host = (parsed.hostname or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""
    lowered = url.lower()

    host_parts = [p for p in host.split(".") if p]
    num_digits = sum(c.isdigit() for c in url)

    return {
        "url_length": len(url),
        "hostname_length": len(host),
        "path_length": len(path),
        "query_length": len(query),
        "num_dots": url.count("."),
        "num_hyphens": url.count("-"),
        "num_underscores": url.count("_"),
        "num_slashes": url.count("/"),
        "num_at": url.count("@"),
        "num_question": url.count("?"),
        "num_equals": url.count("="),
        "num_ampersand": url.count("&"),
        "num_percent": url.count("%"),
        "num_digits": num_digits,
        "digit_ratio": num_digits / len(url) if url else 0.0,
        "has_ip_host": int(bool(IP_PATTERN.match(host))),
        "uses_https": uses_https,
        "has_port": int(parsed.port is not None) if _safe_port(parsed) else 0,
        "num_subdomains": max(len(host_parts) - 2, 0),
        "host_hyphens": host.count("-"),
        "host_digits": sum(c.isdigit() for c in host),
        "host_entropy": _entropy(host),
        "double_slash_in_path": int("//" in path),
        "suspicious_words": sum(w in lowered for w in SUSPICIOUS_WORDS),
        "is_shortener": int(any(host == s or host.endswith("." + s) for s in SHORTENERS)),
        "suspicious_tld": int(host.endswith(SUSPICIOUS_TLDS)),
        "has_punycode": int("xn--" in host),
    }


def _safe_port(parsed):
    try:
        return parsed.port
    except ValueError:
        return None


TRUSTED_PATH = BASE_DIR / "trusted_hosts.txt"


def is_trusted(host):
    """True if the host (or a subdomain of it) is listed in trusted_hosts.txt."""
    if not TRUSTED_PATH.exists():
        return False
    for line in TRUSTED_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        entry = line.split("#")[0].strip().lower()
        if entry.startswith("www."):
            entry = entry[4:]
        if entry and (host == entry or host.endswith("." + entry)):
            return True
    return False


def explain_features(f):
    """Plain-English findings for the UI, based on the domain-name features."""
    reasons = []
    if f["has_ip_host"]:
        reasons.append("The address is a raw IP address instead of a normal domain name.")
    if f["suspicious_tld"]:
        reasons.append("The domain ends with a top-level domain often abused for phishing.")
    if f["has_punycode"]:
        reasons.append("The domain uses punycode (xn--), which can disguise lookalike characters.")
    if f["is_shortener"]:
        reasons.append("The link uses a URL shortener that hides the real destination.")
    if f["suspicious_words"]:
        reasons.append("The domain contains sensitive keywords such as login, verify or secure.")
    if f["num_subdomains"] >= 3:
        reasons.append("The domain has many subdomain levels.")
    if f["host_hyphens"] >= 2:
        reasons.append("The domain contains several hyphens.")
    if f["hostname_length"] >= 30:
        reasons.append("The domain name is unusually long.")
    if f["host_digits"] >= 4:
        reasons.append("The domain contains many digits.")
    if not reasons:
        reasons.append("No common phishing indicators were found in the domain name.")
    return reasons


# ---- Model loading (lazy, cached) ----
_model = None
_feature_names = None


def _load():
    global _model, _feature_names
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        _feature_names = joblib.load(FEATURES_PATH)
    return _model, _feature_names


def predict_url(url):
    """Return a dict with the verdict and confidence for a single URL."""
    if not url or not url.strip():
        raise ValueError("URL must be a non-empty string")

    model, feature_names = _load()
    # The model is trained on hostnames only, so analyse the same form here
    parsed = urlparse(url if "://" in url else "http://" + url)
    host = parsed.hostname or url
    if host.startswith("www."):
        host = host[4:]
    if is_trusted(host):
        return {
            "url": url,
            "is_phishing": False,
            "label": "legitimate",
            "confidence": 1.0,
            "phishing_probability": 0.0,
            "trusted": True,
            "reasons": ["This site is on the trusted list, so the model was not used."],
        }
    features = extract_features(host)
    row = pd.DataFrame([features])[feature_names]

    pred = int(model.predict(row)[0])  # 1 = phishing, 0 = legitimate
    probs = model.predict_proba(row)[0]  # classes_ = [0, 1]
    proba = float(probs[pred])
    phishing_probability = float(probs[1])

    return {
        "url": url,
        "is_phishing": bool(pred),
        "label": "phishing" if pred else "legitimate",
        "confidence": round(proba, 4),
        "phishing_probability": round(phishing_probability, 4),
        "reasons": explain_features(features),
    }


if __name__ == "__main__":
    for u in ["https://www.google.com", "http://192.168.1.5/secure-login/verify.php"]:
        print(predict_url(u))