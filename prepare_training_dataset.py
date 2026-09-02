"""Turn the generated log table into a training-ready CSV.

Run:
    pip install -r requirements.txt
    python prepare_training_dataset.py

Reads smoking_remaining_time_dataset.csv if it still has the full columns,
otherwise smoking_remaining_time_dataset_full.csv.

Writes:
    smoking_remaining_time_dataset_full.csv  (kept as-is)
    smoking_remaining_time_dataset.csv       (X + y + run grouping keys)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from build_smoking_dataset import (
    OUT_CSV,
    OUT_FULL,
    TRAIN_X,
    TRAIN_Y,
    to_training_frame,
)

ROOT = Path(__file__).resolve().parent


def main() -> None:
    candidates = [OUT_CSV, OUT_FULL]
    src = None
    for path in candidates:
        if path.exists():
            peek = pd.read_csv(path, nrows=1)
            if "remaining_min_from_heat" in peek.columns or "target_hours" in peek.columns:
                src = path
                break
    if src is None:
        if not OUT_CSV.exists():
            raise SystemExit("No dataset CSV found. Run build_smoking_dataset.py first.")
        src = OUT_CSV

    full = pd.read_csv(src)
    if "target_hours" in full.columns:
        full.to_csv(OUT_FULL, index=False)
        print(f"Saved full table -> {OUT_FULL}  rows={len(full)}")

    train = to_training_frame(full)
    train.to_csv(OUT_CSV, index=False)
    print(f"Wrote training table -> {OUT_CSV}  rows={len(train)}")
    print(f"TARGET  y = {TRAIN_Y}")
    print("META    run_id, is_synthetic  (GroupKFold / filter only, not features)")
    print(f"X       {TRAIN_X}")


if __name__ == "__main__":
    main()
