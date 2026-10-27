"""
Train the phishing detection model from dataset.csv.
 
Works with BOTH common dataset types (auto-detected):
  1. URL datasets      -> a column with raw URLs + a label column
  2. Feature datasets  -> numeric feature columns + a label column
                          (e.g. the UCI / Kaggle "Phishing Websites" data)
 
Run from the Backend folder:  python train_model.py
"""
 
from pathlib import Path
 
import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
 
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "dataset.csv"
MODEL_PATH = BASE_DIR / "phishing_model.pkl"
FEATURES_PATH = BASE_DIR / "feature_names.pkl"
RANDOM_STATE = 42
 
# Optional: set these manually if auto-detection picks the wrong columns
URL_COL = None
LABEL_COL = None
 
LABEL_NAMES = ("label", "class", "result", "type", "status", "target", "phishing")
URL_NAMES = ("url", "urls", "website", "link", "domain")
PHISHING_VALUES = {"phishing", "bad", "malicious", "malware", "defacement", "spam", "1", "1.0"}
LEGIT_VALUES = {"legitimate", "legit", "good", "benign", "safe", "0", "0.0"}
 
 
def find_column(df, names):
    lower = {c.lower().strip(): c for c in df.columns}
    for n in names:
        if n in lower:
            return lower[n]
    return None
 
 
def to_binary(series):
    """Convert labels to 1 = phishing, 0 = legitimate."""
    values = set(series.astype(str).str.strip().str.lower().unique())
 
    # Numeric -1/1 datasets (UCI): -1 = phishing, 1 = legitimate
    if values <= {"-1", "1", "-1.0", "1.0"}:
        return series.astype(float).map({-1.0: 1, 1.0: 0}).astype(int)
 
    def convert(v):
        v = str(v).strip().lower()
        if v in PHISHING_VALUES:
            return 1
        if v in LEGIT_VALUES:
            return 0
        raise ValueError(f"Unknown label value: {v!r}. Add it to PHISHING_VALUES or LEGIT_VALUES.")
 
    return series.map(convert)
 
 
def build_features(df, label_col, url_col):
    if url_col:
        from detector import extract_features
 
        print(f"Mode: URL dataset (url column = '{url_col}')")
        print("Extracting features from URLs...")
        return pd.DataFrame([extract_features(u) for u in df[url_col]])
 
    print("Mode: precomputed-feature dataset")
    X = df.drop(columns=[label_col])
    X = X.drop(columns=[c for c in X.columns if c.lower() in ("id", "index")], errors="ignore")
    X = X.select_dtypes(include="number")
    if X.empty:
        raise ValueError("No numeric feature columns found and no URL column detected.")
    return X
 
 
def main():
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {DATA_PATH.name}: {df.shape[0]} rows, {df.shape[1]} columns")
    print("Columns:", list(df.columns)[:15], "..." if df.shape[1] > 15 else "")
 
    label_col = LABEL_COL or find_column(df, LABEL_NAMES) or df.columns[-1]
    url_col = URL_COL or find_column(df, URL_NAMES)
    if url_col == label_col:
        url_col = None
    print(f"Label column: '{label_col}'")
 
    df = df.dropna(subset=[label_col]).drop_duplicates()
    if url_col:
        df = df.dropna(subset=[url_col]).drop_duplicates(subset=url_col)
 
    y = to_binary(df[label_col]).reset_index(drop=True)
    X = build_features(df.reset_index(drop=True), label_col, url_col)
 
    print(f"\nSamples: {len(X)}  Features: {X.shape[1]}")
    print("Class balance (0 = legitimate, 1 = phishing):")
    print(y.value_counts(normalize=True).round(3).to_string(), "\n")
 
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )
 
    candidates = {
        "Random Forest": RandomForestClassifier(
            n_estimators=300, class_weight="balanced", n_jobs=-1, random_state=RANDOM_STATE
        ),
        "Gradient Boosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
    }
 
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scores = {}
    for name, model in candidates.items():
        f1 = cross_val_score(model, X_train, y_train, cv=cv, scoring="f1", n_jobs=-1)
        scores[name] = f1.mean()
        print(f"{name:18s} CV F1 = {f1.mean():.4f} (+/- {f1.std():.4f})")
 
    best_name = max(scores, key=scores.get)
    best = candidates[best_name].fit(X_train, y_train)
    print(f"\nBest model: {best_name}")
 
    y_pred = best.predict(X_test)
    print(f"\nTest accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(classification_report(y_test, y_pred, target_names=["legitimate", "phishing"]))
    print("Confusion matrix [[TN FP] [FN TP]]:")
    print(confusion_matrix(y_test, y_pred))
 
    imp = pd.Series(best.feature_importances_, index=X.columns).sort_values(ascending=False)
    print("\nTop 10 features:")
    print(imp.head(10).round(4).to_string())
 
    joblib.dump(best, MODEL_PATH)
    joblib.dump(list(X.columns), FEATURES_PATH)
    print(f"\nSaved {MODEL_PATH.name} and {FEATURES_PATH.name}")
 
 
if __name__ == "__main__":
    main()
 
