import pytest

import detector
from detector import explain_features, extract_features, is_trusted, predict_url

needs_model = pytest.mark.skipif(
    not (detector.MODEL_PATH.exists() and detector.FEATURES_PATH.exists()),
    reason="Trained model files not found. Run train_model.py first.",
)


# ---------- extract_features ----------

def test_returns_27_numeric_features():
    f = extract_features("https://www.google.com")
    assert len(f) == 27
    assert all(isinstance(v, (int, float)) for v in f.values())


def test_normal_https_site():
    f = extract_features("https://www.google.com")
    assert f["uses_https"] == 1
    assert f["has_ip_host"] == 0
    assert f["suspicious_words"] == 0
    assert f["is_shortener"] == 0
    assert f["suspicious_tld"] == 0


def test_ip_address_phishing_url():
    f = extract_features("http://192.168.1.5/secure-login/verify.php")
    assert f["has_ip_host"] == 1
    assert f["uses_https"] == 0
    assert f["suspicious_words"] == 3  # login, verify, secure


def test_url_without_scheme_is_parsed():
    f = extract_features("example.com")
    assert f["hostname_length"] == len("example.com")
    assert f["uses_https"] == 0


def test_subdomain_count():
    assert extract_features("http://a.b.c.example.com")["num_subdomains"] == 3
    assert extract_features("http://example.com")["num_subdomains"] == 0


def test_suspicious_tld():
    assert extract_features("http://free-gift.tk")["suspicious_tld"] == 1


def test_punycode_host():
    assert extract_features("http://xn--pple-43d.com")["has_punycode"] == 1


def test_url_shortener():
    assert extract_features("https://bit.ly/abc123")["is_shortener"] == 1


def test_special_characters_are_counted():
    f = extract_features("http://user@evil-site.com/a?x=1&y=2%20z")
    assert f["num_at"] == 1
    assert f["host_hyphens"] == 1
    assert f["num_question"] == 1
    assert f["num_equals"] == 2
    assert f["num_ampersand"] == 1
    assert f["num_percent"] == 1


def test_port_detection():
    assert extract_features("http://example.com:8080")["has_port"] == 1
    assert extract_features("http://example.com")["has_port"] == 0


def test_invalid_port_does_not_crash():
    assert extract_features("http://example.com:99999")["has_port"] == 0


@pytest.mark.parametrize("value", ["", "   ", None])
def test_empty_or_none_input_does_not_crash(value):
    f = extract_features(value)
    assert f["url_length"] == 0
    assert f["digit_ratio"] == 0.0
    assert f["host_entropy"] == 0.0


def test_very_long_url_does_not_crash():
    f = extract_features("http://example.com/" + "a" * 5000)
    assert f["path_length"] > 5000


def test_random_looking_host_has_higher_entropy():
    plain = extract_features("http://aaaaaaaa.com")["host_entropy"]
    random_like = extract_features("http://q8w3e7r1.com")["host_entropy"]
    assert random_like > plain


# ---------- explain_features ----------

def test_explain_flags_ip_address():
    reasons = explain_features(extract_features("http://192.168.1.5/login"))
    assert any("IP address" in r for r in reasons)


def test_explain_flags_keywords_and_tld():
    reasons = explain_features(extract_features("http://paypal-login.verify-account.tk"))
    assert any("keywords" in r for r in reasons)
    assert any("top-level domain" in r for r in reasons)


def test_explain_clean_domain_gives_single_all_clear_message():
    reasons = explain_features(extract_features("https://example.com"))
    assert reasons == ["No common phishing indicators were found in the domain name."]


# ---------- is_trusted ----------

@pytest.fixture
def trusted_file(tmp_path, monkeypatch):
    path = tmp_path / "trusted_hosts.txt"
    path.write_text(
        "# comment line\n"
        "\n"
        "110.172.151.102   # college website\n"
        "www.example.edu\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(detector, "TRUSTED_PATH", path)
    return path


def test_trusted_exact_ip(trusted_file):
    assert is_trusted("110.172.151.102")


def test_trusted_domain_and_subdomain(trusted_file):
    assert is_trusted("example.edu")
    assert is_trusted("portal.example.edu")


def test_lookalike_domains_are_not_trusted(trusted_file):
    assert not is_trusted("badexample.edu")
    assert not is_trusted("example.edu.evil.com")


def test_unlisted_host_is_not_trusted(trusted_file):
    assert not is_trusted("google.com")


def test_missing_trusted_file_means_nothing_is_trusted(tmp_path, monkeypatch):
    monkeypatch.setattr(detector, "TRUSTED_PATH", tmp_path / "does_not_exist.txt")
    assert not is_trusted("110.172.151.102")


# ---------- predict_url ----------

@pytest.mark.parametrize("value", ["", "   ", None])
def test_predict_url_rejects_empty_input(value):
    with pytest.raises(ValueError):
        predict_url(value)


@needs_model
def test_predict_url_result_structure():
    r = predict_url("https://example.org")
    assert r["label"] in ("phishing", "legitimate")
    assert r["is_phishing"] == (r["label"] == "phishing")
    assert 0.0 <= r["confidence"] <= 1.0
    assert 0.0 <= r["phishing_probability"] <= 1.0
    assert isinstance(r["reasons"], list) and r["reasons"]


@needs_model
def test_www_prefix_is_ignored():
    a = predict_url("https://www.example.org")
    b = predict_url("https://example.org")
    assert a["phishing_probability"] == b["phishing_probability"]


@needs_model
def test_only_the_hostname_is_analysed():
    a = predict_url("https://example.org/a/b/c?x=1")
    b = predict_url("https://example.org")
    assert a["phishing_probability"] == b["phishing_probability"]


@needs_model
def test_trusted_host_skips_the_model(trusted_file):
    r = predict_url("http://110.172.151.102")
    assert r["trusted"] is True
    assert r["is_phishing"] is False
    assert r["phishing_probability"] == 0.0