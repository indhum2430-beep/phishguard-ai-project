"""
Build dataset.csv (columns: url,label) for phishing URL detection.

Phishing URLs   : PhishTank + OpenPhish public feeds
Legitimate URLs : Tranco top-sites list (https://tranco-list.eu)

If a download fails (no internet, blocked, PhishTank needs a key), put your own
files in this folder and the script will use them instead:
    phishing_urls.txt   one phishing URL per line
    legit_domains.txt   one legitimate domain or URL per line

Run from the Backend folder:  python build_dataset.py
"""

import csv
import io
import random
import urllib.request
import zipfile
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).parent
OUT_PATH = BASE_DIR / "dataset.csv"

MAX_PER_CLASS = 10000     # rows per class in the final dataset
TOP_N_LEGIT = 50000       # take legit sites from the top N of the Tranco list
DOMAIN_ONLY = True        # True = keep only the hostname for ALL urls (see note at bottom)
SEED = 42

# Tranco lists bare domains (google.com), while many phishing hosts are subdomains
# (x.weebly.com). To stop the model learning "more dots = phishing", a share of the
# legitimate hosts get a neutral subdomain prefix (blog.example.com). This is
# synthetic augmentation: mention it in your project report.
SUBDOMAIN_SHARE = 0.35
SUBDOMAIN_PREFIXES = ("blog", "mail", "shop", "news", "m", "en", "app", "api", "cdn", "store", "help")

PHISHTANK_URL = "http://data.phishtank.com/data/online-valid.csv"
OPENPHISH_URL = "https://openphish.com/feed.txt"
TRANCO_URL = "https://tranco-list.eu/top-1m.csv.zip"

HEADERS = {"User-Agent": "phishing-detection-student-project"}


def download(url, timeout=60):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def load_phishing():
    urls = []

    try:
        print("Downloading PhishTank feed...")
        text = download(PHISHTANK_URL).decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(text))
        urls += [row["url"].strip() for row in reader if row.get("url")]
        print(f"  PhishTank: {len(urls)} urls")
    except Exception as exc:
        print(f"  PhishTank failed: {exc}")

    try:
        print("Downloading OpenPhish feed...")
        text = download(OPENPHISH_URL).decode("utf-8", errors="ignore")
        found = [line.strip() for line in text.splitlines() if line.strip()]
        urls += found
        print(f"  OpenPhish: {len(found)} urls")
    except Exception as exc:
        print(f"  OpenPhish failed: {exc}")

    local = BASE_DIR / "phishing_urls.txt"
    if local.exists():
        found = [l.strip() for l in local.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip()]
        urls += found
        print(f"  phishing_urls.txt: {len(found)} urls")

    return urls


def load_legit():
    items = []

    try:
        print("Downloading Tranco top sites...")
        data = download(TRANCO_URL, timeout=120)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            name = zf.namelist()[0]
            with zf.open(name) as f:
                for i, line in enumerate(io.TextIOWrapper(f, encoding="utf-8")):
                    if i >= TOP_N_LEGIT:
                        break
                    parts = line.strip().split(",")
                    if len(parts) == 2:
                        items.append(parts[1])
        print(f"  Tranco: {len(items)} domains")
    except Exception as exc:
        print(f"  Tranco failed: {exc}")

    local = BASE_DIR / "legit_domains.txt"
    if local.exists():
        found = [l.strip() for l in local.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip()]
        items += found
        print(f"  legit_domains.txt: {len(found)} entries")

    # Domains -> URLs
    return [i if "://" in i else "https://" + i for i in items]


def clean(urls):
    seen, out = set(), []
    for u in urls:
        u = u.strip()
        if not u or len(u) > 2000:
            continue
        if DOMAIN_ONLY:
            p = urlparse(u if "://" in u else "http://" + u)
            if not p.hostname:
                continue
            u = p.hostname  # hostname only: no scheme, no path
            if u.startswith("www."):
                u = u[4:]  # "www.x.com" and "x.com" are the same site
        key = u.lower()
        if key not in seen:
            seen.add(key)
            out.append(u)
    return out


def main():
    random.seed(SEED)

    phishing = clean(load_phishing())
    legit = clean(load_legit())
    if DOMAIN_ONLY:
        legit = [
            f"{random.choice(SUBDOMAIN_PREFIXES)}.{h}" if random.random() < SUBDOMAIN_SHARE else h
            for h in legit
        ]
    print(f"\nAfter cleaning: {len(phishing)} phishing, {len(legit)} legitimate")

    if not phishing or not legit:
        raise SystemExit(
            "\nCould not get both classes. Check your internet connection, or add "
            "phishing_urls.txt and legit_domains.txt to this folder and run again."
        )

    n = min(len(phishing), len(legit), MAX_PER_CLASS)  # balanced classes
    rows = [(u, "phishing") for u in random.sample(phishing, n)]
    rows += [(u, "legitimate") for u in random.sample(legit, n)]
    random.shuffle(rows)

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "label"])
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} rows ({n} per class) to {OUT_PATH.name}")
    print("Next step: python train_model.py")


if __name__ == "__main__":
    main()

# NOTE on bias: the legitimate URLs come from a domain list (no paths), while real
# phishing URLs often have long paths. A model can then "cheat" by learning that
# long URLs = phishing. If your test accuracy looks suspiciously high (~99%+),
# set DOMAIN_ONLY = True to compare hosts only, and treat results with caution.