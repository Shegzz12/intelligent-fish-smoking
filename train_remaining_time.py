"""Train remaining-time model with leave-one-run-out (no row shuffle leakage).

Run:
    pip install -r requirements.txt
    python train_remaining_time.py

Reads smoking_remaining_time_dataset.csv
Writes remaining_time_model.joblib
"""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold

from build_smoking_dataset import OUT_CSV, TRAIN_X, TRAIN_Y

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "remaining_time_model.joblib"

N_ESTIMATORS = 200
MIN_LEAF = 8
RANDOM_STATE = 0


def load_train() -> pd.DataFrame:
    df = pd.read_csv(OUT_CSV)
    need = ["run_id", "is_synthetic"] + [TRAIN_Y] + TRAIN_X
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise SystemExit(
            f"CSV is missing {missing}. Run prepare_training_dataset.py first."
        )
    return df.dropna(subset=need)


def evaluate_leave_one_run_out(df: pd.DataFrame) -> None:
    X = df[TRAIN_X]
    y = df[TRAIN_Y]
    groups = df["run_id"]
    n_runs = groups.nunique()
    cv = GroupKFold(n_splits=n_runs)

    print(f"Leave-one-run-out  runs={n_runs}  rows={len(df)}")
    print(f"y = {TRAIN_Y}")
    print()

    maes = []
    for fold, (tr, te) in enumerate(cv.split(X, y, groups), start=1):
        held = str(groups.iloc[te].iloc[0])
        synth = int(df.iloc[te]["is_synthetic"].iloc[0])
        model = RandomForestRegressor(
            n_estimators=N_ESTIMATORS,
            min_samples_leaf=MIN_LEAF,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
        model.fit(X.iloc[tr], y.iloc[tr])
        pred = model.predict(X.iloc[te])
        mae = mean_absolute_error(y.iloc[te], pred)
        r2 = r2_score(y.iloc[te], pred)
        maes.append(mae)
        kind = "synth" if synth else "real"
        print(
            f"fold {fold}  hold out {held:16s} ({kind})  "
            f"MAE {mae:7.2f} min  R2 {r2:6.3f}  n={len(te)}"
        )

    print()
    print(f"mean MAE across held-out runs: {np.mean(maes):.2f} min")


def fit_full(df: pd.DataFrame) -> RandomForestRegressor:
    model = RandomForestRegressor(
        n_estimators=N_ESTIMATORS,
        min_samples_leaf=MIN_LEAF,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(df[TRAIN_X], df[TRAIN_Y])
    imp = pd.Series(model.feature_importances_, index=TRAIN_X).sort_values(ascending=False)
    print()
    print("Feature importance (full fit):")
    print(imp.to_string())
    payload = {
        "model": model,
        "features": list(TRAIN_X),
        "target": TRAIN_Y,
    }
    joblib.dump(payload, MODEL_PATH)
    print()
    print(f"Wrote {MODEL_PATH}")
    return model


def main() -> None:
    df = load_train()
    print("Do not put run_id or is_synthetic into X. Group splits by run_id.")
    print()
    evaluate_leave_one_run_out(df)
    fit_full(df)


if __name__ == "__main__":
    main()
