#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Apex Quant ML — One-shot training script
# Trains the 4-model ensemble without Snakemake.
# Usage:  bash scripts/train_models.sh
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MODELS_DIR="$PROJECT_DIR/models/quant"

echo "═══ Apex Quant ML Training ═══"
echo "Models dir: $MODELS_DIR"
echo ""

# ── Step 1: Fetch data ─────────────────────────────────────────────────────
echo "─── Step 1: Fetching OHLCV data ───"
mkdir -p "$MODELS_DIR"

uv run python3 << 'PYEOF'
import os, sys
sys.path.insert(0, os.getcwd())

import yfinance as yf
import pandas as pd

TICKERS = ["AAPL", "MSFT", "NVDA", "TSLA", "SPY"]
MODELS_DIR = "models/quant"
os.makedirs(MODELS_DIR, exist_ok=True)

all_bars = []
for ticker in TICKERS:
    df = yf.download(ticker, period="5y", auto_adjust=True)
    if df.empty:
        print(f"WARNING: no data for {ticker}, skipping")
        continue
    df = df.reset_index()
    df["ticker"] = ticker
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if col[1] == "" else col[0] for col in df.columns]
    all_bars.append(df)
    print(f"Fetched {len(df)} bars for {ticker}")

if not all_bars:
    print("ERROR: no data fetched")
    sys.exit(1)

combined = pd.concat(all_bars, ignore_index=True)
combined.to_parquet(f"{MODELS_DIR}/raw_data.parquet")
print(f"Saved {len(combined)} total bars to {MODELS_DIR}/raw_data.parquet")
PYEOF

# ── Step 2: Engineer features ──────────────────────────────────────────────
echo ""
echo "─── Step 2: Engineering features ───"

uv run python3 << 'PYEOF'
import os, sys
sys.path.insert(0, os.getcwd())

import numpy as np
import pandas as pd

MODELS_DIR = "models/quant"
df = pd.read_parquet(f"{MODELS_DIR}/raw_data.parquet")

feature_rows = []
for ticker, group in df.groupby("ticker"):
    grp = group.sort_values("Date").reset_index(drop=True)
    close = grp["Close"].astype(float).values
    high = grp["High"].astype(float).values
    low = grp["Low"].astype(float).values
    vol = grp["Volume"].astype(float).values
    n = len(close)

    features = {col: [] for col in [
        "return_1d", "return_5d", "return_21d",
        "volatility_5d", "volatility_21d",
        "close_high_ratio", "close_low_ratio", "high_low_ratio",
        "rsi_14", "macd", "macd_signal", "macd_histogram",
        "bollinger_pctb", "sma20_ratio", "sma50_ratio",
        "volume_ratio", "volume_price_trend",
        "rolling_min_5d", "rolling_max_5d", "rolling_mean_5d",
        "rolling_min_21d", "rolling_max_21d", "rolling_mean_21d",
    ]}

    def _ema_arr(data, span):
        k = 2.0 / (span + 1)
        result = [float(data[0])]
        for v in data[1:]:
            result.append(v * k + result[-1] * (1 - k))
        return np.array(result)

    for i in range(n):
        features["return_1d"].append(float(close[i] / close[i - 1] - 1) if i >= 1 else 0.0)
        features["return_5d"].append(float(close[i] / close[i - 5] - 1) if i >= 5 else 0.0)
        features["return_21d"].append(float(close[i] / close[i - 21] - 1) if i >= 21 else 0.0)
        features["volatility_5d"].append(float(np.std(close[max(0, i - 4):i + 1])))
        features["volatility_21d"].append(float(np.std(close[max(0, i - 20):i + 1])))
        features["close_high_ratio"].append(float(close[i] / high[i]) if high[i] else 0.0)
        features["close_low_ratio"].append(float(close[i] / low[i]) if low[i] else 0.0)
        features["high_low_ratio"].append(float(high[i] / low[i]) if low[i] else 0.0)

        if i >= 14:
            gains, losses = [], []
            for j in range(i - 13, i + 1):
                ch = close[j] - close[j - 1]
                gains.append(max(ch, 0))
                losses.append(max(-ch, 0))
            avg_g = np.mean(gains)
            avg_l = np.mean(losses)
            rs = avg_g / avg_l if avg_l > 0 else 100.0
            features["rsi_14"].append(float(100 - 100 / (1 + rs)))
        else:
            features["rsi_14"].append(50.0)

        if i >= 26:
            win = close[:i + 1]
            ema12 = _ema_arr(win, 12)[-1]
            ema26 = _ema_arr(win, 26)[-1]
            md = ema12 - ema26
            sig_win = []
            for j in range(max(0, i - 8), i + 1):
                sub = close[:j + 1]
                e12 = _ema_arr(sub, 12)[-1]
                e26 = _ema_arr(sub, 26)[-1]
                sig_win.append(e12 - e26)
            sig = _ema_arr(np.array(sig_win), 9)[-1] if len(sig_win) >= 9 else 0.0
            features["macd"].append(md)
            features["macd_signal"].append(sig)
            features["macd_histogram"].append(md - sig)
        else:
            features["macd"].append(0.0)
            features["macd_signal"].append(0.0)
            features["macd_histogram"].append(0.0)

        if i >= 20:
            win = close[i - 19:i + 1]
            sma20 = np.mean(win)
            std20 = np.std(win)
            upper = sma20 + 2 * std20
            lower = sma20 - 2 * std20
            pctb = (close[i] - lower) / (upper - lower) if (upper - lower) > 0 else 0.5
            features["bollinger_pctb"].append(float(pctb))
        else:
            features["bollinger_pctb"].append(0.5)

        if i >= 20:
            sma20 = float(np.mean(close[i - 19:i + 1]))
            features["sma20_ratio"].append(float(close[i] / sma20 - 1 if sma20 else 0.0))
        else:
            features["sma20_ratio"].append(0.0)
        if i >= 50:
            sma50 = float(np.mean(close[i - 49:i + 1]))
            features["sma50_ratio"].append(float(close[i] / sma50 - 1 if sma50 else 0.0))
        else:
            features["sma50_ratio"].append(0.0)

        if i >= 21:
            avg_vol = float(np.mean(vol[i - 20:i + 1]))
            features["volume_ratio"].append(float(vol[i] / avg_vol) if avg_vol else 1.0)
        else:
            features["volume_ratio"].append(1.0)

        if i >= 1:
            features["volume_price_trend"].append(float(vol[i] * (close[i] - close[i - 1]) / close[i - 1]) if close[i - 1] else 0.0)
        else:
            features["volume_price_trend"].append(0.0)

        features["rolling_min_5d"].append(float(np.min(close[max(0, i - 4):i + 1])))
        features["rolling_max_5d"].append(float(np.max(close[max(0, i - 4):i + 1])))
        features["rolling_mean_5d"].append(float(np.mean(close[max(0, i - 4):i + 1])))
        features["rolling_min_21d"].append(float(np.min(close[max(0, i - 20):i + 1])))
        features["rolling_max_21d"].append(float(np.max(close[max(0, i - 20):i + 1])))
        features["rolling_mean_21d"].append(float(np.mean(close[max(0, i - 20):i + 1])))

    feat_df = pd.DataFrame(features)
    feat_df["ticker"] = ticker
    feat_df["Date"] = grp["Date"]

    y_arr = np.zeros(n)
    for i in range(n - 1):
        y_arr[i] = 1.0 if close[i + 1] > close[i] else 0.0
    feat_df["target"] = y_arr
    feature_rows.append(feat_df)

result = pd.concat(feature_rows, ignore_index=True)
result = result.dropna().reset_index(drop=True)
result.to_parquet(f"{MODELS_DIR}/features.parquet")
print(f"Engineered {len(result)} feature vectors")
PYEOF

# ── Step 3: Train models ──────────────────────────────────────────────────
echo ""
echo "─── Step 3: Training models ───"

uv run python3 << 'PYEOF'
import os, sys, json, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.getcwd())

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import RidgeCV
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, confusion_matrix, classification_report)
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
import joblib

MODELS_DIR = "models/quant"

df = pd.read_parquet(f"{MODELS_DIR}/features.parquet")
feature_cols = [c for c in df.columns if c not in ("ticker", "Date", "target")]
X = df[feature_cols].values
y = df["target"].values

split_idx = int(len(X) * 0.8)
X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Train: {len(X_train)} samples, Test: {len(X_test)} samples")
print(f"Features: {len(feature_cols)}")

# Random Forest
print("\n--- Random Forest ---")
rf = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)
rf.fit(X_train_scaled, y_train)

# XGBoost
print("\n--- XGBoost ---")
import xgboost as xgb
xgb_model = xgb.XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1,
                               random_state=42, verbosity=0)
xgb_model.fit(X_train_scaled, y_train)

# LightGBM
print("\n--- LightGBM ---")
import lightgbm as lgbm
lgbm_model = lgbm.LGBMClassifier(n_estimators=200, max_depth=6, learning_rate=0.1,
                                   random_state=42, verbose=-1)
lgbm_model.fit(X_train_scaled, y_train)

# CatBoost
print("\n--- CatBoost ---")
from catboost import CatBoostClassifier
cb_model = CatBoostClassifier(iterations=200, depth=6, learning_rate=0.1,
                                random_seed=42, verbose=False)
cb_model.fit(X_train_scaled, y_train)

# RidgeCV meta-learner
print("\n--- RidgeCV Ensemble Voter ---")
tscv = TimeSeriesSplit(n_splits=3)
meta_train = np.zeros((len(X_train_scaled), 4))
for train_idx, val_idx in tscv.split(X_train_scaled):
    X_fold = X_train_scaled[train_idx]
    y_fold = y_train[train_idx]
    X_val = X_train_scaled[val_idx]

    fold_rf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42, n_jobs=-1)
    fold_rf.fit(X_fold, y_fold)
    meta_train[val_idx, 0] = fold_rf.predict_proba(X_val)[:, 1]

    fold_xgb = xgb.XGBClassifier(n_estimators=100, max_depth=4, random_state=42, verbosity=0)
    fold_xgb.fit(X_fold, y_fold)
    meta_train[val_idx, 1] = fold_xgb.predict_proba(X_val)[:, 1]

    fold_lgbm = lgbm.LGBMClassifier(n_estimators=100, max_depth=4, random_state=42, verbose=-1)
    fold_lgbm.fit(X_fold, y_fold)
    meta_train[val_idx, 2] = fold_lgbm.predict_proba(X_val)[:, 1]

    fold_cb = CatBoostClassifier(iterations=100, depth=4, random_seed=42, verbose=False)
    fold_cb.fit(X_fold, y_fold)
    meta_train[val_idx, 3] = fold_cb.predict_proba(X_val)[:, 1]

ridge = RidgeCV(alphas=[0.01, 0.1, 1.0, 10.0])
ridge.fit(meta_train, y_train)
print(f"RidgeCV best alpha: {ridge.alpha_}")

# Evaluate
meta_test = np.column_stack([
    rf.predict_proba(X_test_scaled)[:, 1],
    xgb_model.predict_proba(X_test_scaled)[:, 1],
    lgbm_model.predict_proba(X_test_scaled)[:, 1],
    cb_model.predict_proba(X_test_scaled)[:, 1],
])
ensemble_probs = ridge.predict(meta_test)
ensemble_preds = (ensemble_probs >= 0.5).astype(int)

print("\n" + "=" * 60)
print("EVALUATION")
print("=" * 60)

for name, model in [("RF", rf), ("XGB", xgb_model), ("LGBM", lgbm_model), ("CB", cb_model)]:
    preds = model.predict(X_test_scaled)
    print(f"\n{name}:")
    print(f"  Acc={accuracy_score(y_test, preds):.4f}  Prec={precision_score(y_test, preds, zero_division=0):.4f}  Rec={recall_score(y_test, preds, zero_division=0):.4f}  F1={f1_score(y_test, preds, zero_division=0):.4f}")

print(f"\nEnsemble:")
print(f"  Acc={accuracy_score(y_test, ensemble_preds):.4f}  Prec={precision_score(y_test, ensemble_preds, zero_division=0):.4f}  Rec={recall_score(y_test, ensemble_preds, zero_division=0):.4f}  F1={f1_score(y_test, ensemble_preds, zero_division=0):.4f}")

# Save
joblib.dump(rf, f"{MODELS_DIR}/random_forest.pkl")
joblib.dump(xgb_model, f"{MODELS_DIR}/xgboost.pkl")
joblib.dump(lgbm_model, f"{MODELS_DIR}/lightgbm.pkl")
joblib.dump(cb_model, f"{MODELS_DIR}/catboost.pkl")
joblib.dump(ridge, f"{MODELS_DIR}/ensemble_voter.pkl")
joblib.dump(scaler, f"{MODELS_DIR}/scaler.pkl")

# Metadata
metadata = {
    "model_version": "rf+xgb+lgbm+cb_v1",
    "features": feature_cols,
    "n_estimators": 200,
    "ensemble": "RidgeCV",
    "n_train": int(len(X_train)),
    "n_test": int(len(X_test)),
    "train_date": str(pd.Timestamp.now().date()),
    "tickers": ["AAPL", "MSFT", "NVDA", "TSLA", "SPY"],
}
with open(f"{MODELS_DIR}/metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print(f"\nModels saved to {MODELS_DIR}/")
PYEOF

echo ""
echo "═══ Training complete ═══"
echo "Models: $MODELS_DIR"
ls -lh "$MODELS_DIR"/*.pkl 2>/dev/null || echo "(no pkl files — training may have failed)"
