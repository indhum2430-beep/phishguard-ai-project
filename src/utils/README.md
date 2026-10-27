# PhishGuard AI: Intelligent Phishing Website Detection using ML

A web app that checks a URL with a trained machine-learning model and shows a
risk score, a risk level and the findings behind it.

- **Frontend:** React + Vite
- **Backend:** Python + Flask
- **Model:** Gradient Boosting (scikit-learn) trained on features of the domain name

## Project structure

```
phishguard-ai/
├── src/                     React app (App.jsx is the main page)
├── Backend/
│   ├── app.py               Flask API (/api/scan, /predict, /health)
│   ├── detector.py          Feature extraction + prediction
│   ├── build_dataset.py     Builds dataset.csv from public feeds
│   ├── train_model.py       Trains and evaluates the model
│   ├── trusted_hosts.txt    Sites that skip the model (one per line)
│   ├── requirements.txt
│   └── tests/               pytest unit tests
└── package.json
```

## How to run

You need two terminals open at the same time.

**Terminal 1: backend**

```
cd Backend
python -m pip install -r requirements.txt
python app.py
```

The API runs on `http://127.0.0.1:5000`.

**Terminal 2: frontend**

```
npm install
npm run dev
```

Open the address Vite prints (usually `http://localhost:5173`) and use the
**Scanner** page.

## Training the model

Run from the `Backend` folder:

```
python build_dataset.py     # downloads phishing + legitimate URLs -> dataset.csv
python train_model.py       # trains, evaluates, saves phishing_model.pkl and feature_names.pkl
```

Data sources: PhishTank and OpenPhish (phishing URLs), Tranco top-sites list
(legitimate domains).

## API

`POST /api/scan` with `{"url": "https://example.com"}` returns:

```json
{
  "url": "https://example.com",
  "score": 10,
  "status": "SAFE",
  "label": "legitimate",
  "is_phishing": false,
  "confidence": 90,
  "latency": 25,
  "reasons": ["Machine-learning model estimates a 10% chance this site is phishing."]
}
```

`GET /health` returns `{"status": "ok"}`.

## Tests

```
cd Backend
python -m pip install pytest
python -m pytest -v
```

## Results

| Metric (held-out test set) | Value |
|---|---|
| Accuracy | about 84% |
| Phishing precision | 0.89 |
| Phishing recall | 0.77 |

An earlier run scored 99.4%, but the top features were `num_slashes` and
`path_length`. The legitimate URLs were bare domains while many phishing URLs
had long paths, so the model was learning the dataset, not phishing. The model
was retrained on hostnames only (no scheme, path or `www.`), and the score
dropped to the honest value above.

## Limitations

- The model analyses the **domain name only**. It does not fetch the page,
  check certificates, WHOIS age or page content.
- Some legitimate training hosts have synthetic subdomain prefixes (such as
  `blog.`) added, to stop the model learning that extra dots mean phishing.
- Raw IP addresses are mostly phishing in the training data, so legitimate
  sites hosted on a bare IP can be flagged (a false positive). Such sites can be
  added to `Backend/trusted_hosts.txt`, which skips the model for them.
- Scan history on the Dashboard is kept only for the current browser session.
- A low score does not guarantee that a website is safe.

## Future work

- Add hostname character n-gram features to catch lookalike domains.
- Add page-content and WHOIS-based features.
- Collect a labelled dataset of legitimate URLs that include paths and subdomains.