"""Train multi-fish remaining-time model with fish type as feature.

Combines datasets from shawa, catfish, and tuna fish.
Includes fish_type as a categorical feature for the model to distinguish between fish types.

Run:
    pip install -r requirements.txt
    python train_multi_fish_model.py

Reads:
    - smoking_remaining_time_dataset.csv (shawa fish)
    - catfish_smoking_remaining_time_dataset.csv (catfish)
    - tuna_smoking_remaining_time_dataset.csv (tuna)

Writes multi_fish_remaining_time_model.joblib
"""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import LabelEncoder

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "multi_fish_remaining_time_model.joblib"

# Dataset paths
SHAWA_DATASET = ROOT / "smoking_remaining_time_dataset.csv"
CATFISH_DATASET = ROOT / "catfish_smoking_remaining_time_dataset.csv"
TUNA_DATASET = ROOT / "tuna_smoking_remaining_time_dataset.csv"

N_ESTIMATORS = 200
MIN_LEAF = 8
RANDOM_STATE = 0

# Features for the model (including fish_type)
TRAIN_X = [
    "fish_type",
    "start_weight_g",
    "elapsed_smoking_min",
    "oven_temp_c",
    "oven_deg_h",
    "dht11_temp_c",
    "dht11_humidity_pct",
    "mq6_adc",
    "mq6_ratio",
    "weight_corrected_g",
    "weight_smooth_g",
    "weight_loss_from_start_g",
    "moisture_removed_frac",
    "drying_rate_g_per_min",
]

TRAIN_Y = "remaining_min"


def load_and_combine_datasets() -> pd.DataFrame:
    """Load and combine the three fish datasets with fish type labels."""
    print("Loading datasets...")
    
    # Load shawa fish dataset
    shawa_df = pd.read_csv(SHAWA_DATASET)
    shawa_df["fish_type"] = "shawa"
    print(f"Shawa fish: {len(shawa_df)} rows")
    
    # Load catfish dataset
    catfish_df = pd.read_csv(CATFISH_DATASET)
    catfish_df["fish_type"] = "catfish"
    print(f"Catfish: {len(catfish_df)} rows")
    
    # Load tuna fish dataset
    tuna_df = pd.read_csv(TUNA_DATASET)
    tuna_df["fish_type"] = "tuna"
    print(f"Tuna fish: {len(tuna_df)} rows")
    
    # Combine all datasets
    combined_df = pd.concat([shawa_df, catfish_df, tuna_df], ignore_index=True)
    print(f"Combined dataset: {len(combined_df)} rows")
    
    # Ensure all required columns exist
    required_cols = ["run_id", "is_synthetic", TRAIN_Y] + TRAIN_X
    missing_cols = [col for col in required_cols if col not in combined_df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in combined dataset: {missing_cols}")
    
    # Remove rows with missing values in required columns
    combined_df = combined_df.dropna(subset=required_cols)
    print(f"After cleaning: {len(combined_df)} rows")
    
    return combined_df


def encode_fish_type(df: pd.DataFrame) -> tuple[pd.DataFrame, LabelEncoder]:
    """Encode fish_type as numerical feature for the model."""
    le = LabelEncoder()
    df["fish_type_encoded"] = le.fit_transform(df["fish_type"])
    
    # Update feature list to use encoded version
    feature_list = [col if col != "fish_type" else "fish_type_encoded" for col in TRAIN_X]
    
    print(f"Fish type encoding: {dict(zip(le.classes_, le.transform(le.classes_)))}")
    return df, le, feature_list


def evaluate_leave_one_run_out(df: pd.DataFrame, feature_list: list) -> None:
    """Evaluate model using leave-one-run-out cross-validation."""
    X = df[feature_list]
    y = df[TRAIN_Y]
    groups = df["run_id"]
    n_runs = groups.nunique()
    cv = GroupKFold(n_splits=n_runs)

    print(f"\nLeave-one-run-out evaluation:")
    print(f"Runs: {n_runs}, Rows: {len(df)}")
    print(f"Target: {TRAIN_Y}")
    print(f"Features: {feature_list}")
    print()

    maes = []
    for fold, (tr, te) in enumerate(cv.split(X, y, groups), start=1):
        held_run = str(groups.iloc[te].iloc[0])
        synth = int(df.iloc[te]["is_synthetic"].iloc[0])
        fish_type = df.iloc[te]["fish_type"].iloc[0]
        
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
            f"Fold {fold:2d} | Hold: {held_run:20s} ({kind:5s}) | "
            f"Fish: {fish_type:8s} | MAE: {mae:6.2f} min | R²: {r2:6.3f} | n: {len(te):4d}"
        )

    print()
    print(f"Mean MAE across held-out runs: {np.mean(maes):.2f} min")
    print(f"Std MAE across held-out runs: {np.std(maes):.2f} min")


def fit_full_model(df: pd.DataFrame, feature_list: list, label_encoder: LabelEncoder) -> RandomForestRegressor:
    """Train the final model on all data."""
    print("\nTraining final model on all data...")
    
    model = RandomForestRegressor(
        n_estimators=N_ESTIMATORS,
        min_samples_leaf=MIN_LEAF,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    
    X = df[feature_list]
    y = df[TRAIN_Y]
    model.fit(X, y)
    
    # Feature importance
    imp = pd.Series(model.feature_importances_, index=feature_list).sort_values(ascending=False)
    print("\nFeature importance:")
    print(imp.to_string())
    
    # Save model with metadata
    payload = {
        "model": model,
        "features": feature_list,
        "target": TRAIN_Y,
        "fish_type_encoder": label_encoder,
        "fish_type_classes": list(label_encoder.classes_),
        "model_type": "multi_fish",
        "n_estimators": N_ESTIMATORS,
        "min_samples_leaf": MIN_LEAF,
    }
    
    joblib.dump(payload, MODEL_PATH)
    print(f"\nModel saved to: {MODEL_PATH}")
    
    return model


def main() -> None:
    print("=" * 60)
    print("Multi-Fish Remaining Time Model Training")
    print("=" * 60)
    
    # Load and combine datasets
    df = load_and_combine_datasets()
    
    # Encode fish type
    df, label_encoder, feature_list = encode_fish_type(df)
    
    # Evaluate with cross-validation
    evaluate_leave_one_run_out(df, feature_list)
    
    # Train final model
    fit_full_model(df, feature_list, label_encoder)
    
    print("\n" + "=" * 60)
    print("Training complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()