"""Build remaining-time dataset from catfish smoking experiments.

Run:
    pip install -r requirements.txt
    python build_catfish_dataset.py

Writes catfish_smoking_remaining_time_dataset_full.csv (all columns) and
catfish_smoking_remaining_time_dataset.csv (training-ready: no leakage).
"""
from __future__ import annotations

import math
import re
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(r"C:\Users\NICK\Downloads\intelligent-fish-smoking-main\intelligent-fish-smoking-main")
# Catfish data file paths - using the main data file
CATFISH_DATA = ROOT / "cat_fish_datas"

OUT_FULL = ROOT / "catfish_smoking_remaining_time_dataset_full.csv"
OUT_CSV = ROOT / "catfish_smoking_remaining_time_dataset.csv"

# Live sensors + load size. Do not put target_* / remaining_min_from_* / *_progress_frac in X.
TRAIN_META = ["run_id", "is_synthetic"]
TRAIN_Y = "remaining_min"
TRAIN_X = [
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

HEAT_DONE = 0.98
WEIGHT_DONE = 0.98
MIN_OVEN_FOR_ETA = 80.0

# Catfish experiment parameters - based on actual data
CATFISH_START = pd.Timestamp("2026-08-31 11:46:40")  # Start of main catfish smoking
CATFISH_END = pd.Timestamp("2026-08-31 12:15:30")    # End of main catfish smoking  
CATFISH_W0 = 3342.0  # Starting weight in grams (from real data: ~3342.3g)
# Ending weight will be determined from actual data

SYNTH_LOADS_G = (800.0, 6000.0, 10000.0)  # Synthetic load sizes to generate

COLS = [
    "timestamp",
    "dht11_temp_c",
    "dht11_humidity_pct",
    "oven_temp_c",
    "mq6_adc",
    "mq6_ratio",
    "weight_g",
]
LINE_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),"
    r"([-\d.]+),([-\d.]+),([-\d.]+),([-\d.]+),([-\d.]+),([-\d.]+)"
)

KEEP = [
    "run_id",
    "is_synthetic",
    "session",
    "timestamp",
    "elapsed_smoking_min",
    "remaining_min",
    "remaining_min_from_heat",
    "remaining_min_from_weight",
    "remaining_min_gated",
    "start_weight_g",
    "dht11_temp_c",
    "dht11_humidity_pct",
    "oven_temp_c",
    "mq6_adc",
    "mq6_ratio",
    "weight_g",
    "weight_corrected_g",
    "weight_smooth_g",
    "weight_loss_from_start_g",
    "moisture_removed_frac",
    "target_loss_frac",
    "weight_progress_frac",
    "drying_rate_g_per_min",
    "oven_deg_h",
    "target_oven_deg_h",
    "heat_progress_frac",
    "target_hours",
]


def load_log(path: Path) -> pd.DataFrame:
    rows = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        m = LINE_RE.search(line)
        if not m:
            continue
        ts = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
        vals = [float(x) for x in m.groups()[1:]]
        rows.append((ts, *vals))
    df = pd.DataFrame(rows, columns=COLS)
    return (
        df.drop_duplicates(subset=["timestamp"])
        .sort_values("timestamp")
        .reset_index(drop=True)
    )


def fill_weight_dropouts(w: np.ndarray, min_fish_g: float = 400.0) -> np.ndarray:
    out = w.copy()
    last = np.nan
    for i, v in enumerate(out):
        if v >= min_fish_g:
            last = v
        elif not np.isnan(last):
            nxt = any(out[j] >= min_fish_g for j in range(i + 1, min(i + 6, len(out))))
            if nxt:
                out[i] = last
    return out


def reanchor_steps(weights: np.ndarray, jump_g: float = 80.0, hold: int = 4) -> np.ndarray:
    w = weights.copy()
    offset = 0.0
    out = np.empty_like(w)
    out[0] = w[0]
    for i in range(1, len(w)):
        dw = (w[i] + offset) - out[i - 1]
        if abs(dw) >= jump_g and i + hold < len(w):
            future = w[i : i + hold]
            if np.max(np.abs(np.diff(future))) < jump_g / 2:
                offset = out[i - 1] - w[i]
        out[i] = w[i] + offset
    return out


def add_clock(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    dt = out.timestamp.diff().dt.total_seconds().fillna(0).clip(lower=0, upper=30)
    out["dt_s"] = dt
    out["elapsed_smoking_min"] = dt.cumsum() / 60.0
    t_end = float(out.elapsed_smoking_min.iloc[-1])
    out["remaining_min"] = t_end - out.elapsed_smoking_min
    return out, t_end


def add_weight_and_heat(df: pd.DataFrame, w0: float) -> pd.DataFrame:
    out = df.copy()
    out["start_weight_g"] = w0
    out["weight_smooth_g"] = out.weight_corrected_g.rolling(
        12, min_periods=1, center=True
    ).median()
    out["weight_loss_from_start_g"] = w0 - out.weight_corrected_g
    out["moisture_removed_frac"] = out.weight_loss_from_start_g / w0
    out["drying_rate_g_per_min"] = (
        out.weight_smooth_g.diff() / out.elapsed_smoking_min.diff().replace(0, np.nan)
    ).rolling(24, min_periods=4).median()
    out["drying_rate_g_per_min"] = out["drying_rate_g_per_min"].fillna(0.0)
    out["oven_deg_h"] = (out.oven_temp_c * (out.dt_s / 3600.0)).cumsum()
    return out


def add_targets_and_gates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    target_deg_h = float(out.oven_deg_h.iloc[-1])
    target_loss_frac = max(float(out.moisture_removed_frac.iloc[-1]), 1e-6)
    t_end = float(out.elapsed_smoking_min.iloc[-1])
    w0 = float(out.start_weight_g.iloc[0])

    out["target_oven_deg_h"] = target_deg_h
    out["target_loss_frac"] = target_loss_frac
    out["target_hours"] = t_end / 60.0
    out["heat_progress_frac"] = out.oven_deg_h / max(target_deg_h, 1e-6)
    progress = (out.moisture_removed_frac / target_loss_frac).clip(lower=0)
    out["weight_progress_frac"] = progress

    leftover_deg_h = (target_deg_h - out.oven_deg_h).clip(lower=0)
    out["remaining_min_from_heat"] = (
        leftover_deg_h / out.oven_temp_c.clip(lower=MIN_OVEN_FOR_ETA) * 60.0
    )
    loss_rate = (-out.drying_rate_g_per_min).clip(lower=0.05)
    leftover_g = (target_loss_frac * w0 - out.weight_loss_from_start_g).clip(lower=0)
    out["remaining_min_from_weight"] = leftover_g / loss_rate
    out.loc[out.drying_rate_g_per_min.isna(), "remaining_min_from_weight"] = out.remaining_min

    both_ok = (out.heat_progress_frac >= HEAT_DONE) & (out.weight_progress_frac >= WEIGHT_DONE)
    out["remaining_min_gated"] = np.where(
        both_ok,
        0.0,
        np.maximum.reduce(
            [
                out.remaining_min.to_numpy(),
                out.remaining_min_from_heat.to_numpy(),
                out.remaining_min_from_weight.fillna(out.remaining_min).to_numpy(),
            ]
        ),
    )
    return out


def drying_progress(df: pd.DataFrame) -> np.ndarray:
    """0→1 dryness using this cook; never goes backwards."""
    frac = df.moisture_removed_frac.to_numpy(dtype=float)
    target = max(float(df.target_loss_frac.iloc[-1]), 1e-6)
    p = np.clip(frac / target, 0.0, 1.0)
    return np.maximum.accumulate(p)


def build_catfish_main() -> pd.DataFrame:
    """Build the main catfish smoking dataset from experimental data."""
    # Load the main catfish smoking data from cat_fish_datas
    main_data = load_log(CATFISH_DATA)
    
    # Filter to the smoking period
    df = main_data[
        (main_data.timestamp >= CATFISH_START) & 
        (main_data.timestamp <= CATFISH_END)
    ].copy()
    
    df["session"] = "catfish_main"
    
    # Fill weight dropouts and reanchor steps
    df["weight_filled_g"] = fill_weight_dropouts(df.weight_g.to_numpy())
    df["weight_corrected_g"] = reanchor_steps(df.weight_filled_g.to_numpy())
    
    # Add timing information
    df, t_end = add_clock(df)
    
    # Use the actual starting weight from the data
    w0 = float(df.weight_corrected_g.iloc[0])
    
    # Add weight and heat calculations
    df = add_weight_and_heat(df, w0)
    
    # Add targets and gates
    df = add_targets_and_gates(df)
    
    df["run_id"] = "catfish_3342g"  # Use actual starting weight in run_id
    df["is_synthetic"] = 0
    
    print(
        f"catfish_3342g  {t_end:.1f} min  {w0:.0f}→{df.weight_corrected_g.iloc[-1]:.0f} g  "
        f"loss {(w0 - df.weight_corrected_g.iloc[-1])/w0*100:.1f}%  "
        f"{df.target_oven_deg_h.iloc[-1]:.0f} °C·h"
    )
    return df


def power_law_fit(m_a: float, y_a: float, m_b: float, y_b: float):
    """y = a * m ** k  through two measured points."""
    k = math.log(y_b / y_a) / math.log(m_b / m_a)
    a = y_a / (m_a ** k)
    return a, k


def predict_power(a: float, k: float, m: float) -> float:
    return a * (m ** k)


def synthesize_from_template(
    template: pd.DataFrame,
    mass_g: float,
    t_new_min: float,
    loss_frac: float,
    run_id: str,
) -> pd.DataFrame:
    t_ref = float(template.elapsed_smoking_min.iloc[-1])
    scale_t = t_new_min / t_ref
    p = drying_progress(template)

    out = template.copy()
    out["run_id"] = run_id
    out["is_synthetic"] = 1
    out["session"] = "synth"
    out["elapsed_smoking_min"] = template.elapsed_smoking_min * scale_t
    out["remaining_min"] = t_new_min - out.elapsed_smoking_min
    out["dt_s"] = template.dt_s * scale_t

    w = mass_g * (1.0 - loss_frac * p)
    out["start_weight_g"] = mass_g
    out["weight_corrected_g"] = w
    out["weight_g"] = w
    out["weight_smooth_g"] = pd.Series(w).rolling(12, min_periods=1, center=True).median().to_numpy()
    out["weight_loss_from_start_g"] = mass_g - w
    out["moisture_removed_frac"] = (mass_g - w) / mass_g
    out["drying_rate_g_per_min"] = (
        pd.Series(out["weight_smooth_g"]).diff()
        / pd.Series(out["elapsed_smoking_min"]).diff().replace(0, np.nan)
    ).rolling(24, min_periods=4).median().fillna(0.0).to_numpy()

    out["oven_deg_h"] = template.oven_deg_h * scale_t
    t0 = datetime(2099, 1, 1, 0, 0, 0)
    out["timestamp"] = [
        t0 + timedelta(minutes=float(x)) for x in out.elapsed_smoking_min
    ]
    out = add_targets_and_gates(out)
    print(
        f"{run_id}  {t_new_min:.1f} min ({t_new_min/60:.2f} h)  "
        f"{mass_g:.0f}→{w[-1]:.0f} g  loss {loss_frac*100:.1f}%  "
        f"{out.target_oven_deg_h.iloc[-1]:.0f} °C·h"
    )
    return out


def to_training_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Drop leaky/id columns, impute start-of-run rates, remove broken rows."""
    out = df.copy()
    if "drying_rate_g_per_min" in out.columns:
        out["drying_rate_g_per_min"] = out["drying_rate_g_per_min"].fillna(0.0)

    need = TRAIN_META + [TRAIN_Y] + TRAIN_X
    missing = [c for c in need if c not in out.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    out = out[need]
    num = TRAIN_X + [TRAIN_Y]
    out[num] = out[num].replace([np.inf, -np.inf], np.nan)

    ok = (
        out[TRAIN_Y].notna()
        & (out[TRAIN_Y] >= 0)
        & (out["start_weight_g"] > 0)
        & (out["weight_corrected_g"] > 0)
        & (out["weight_smooth_g"] > 0)
        & (out["oven_temp_c"] > 0)
        & (out["oven_temp_c"] < 800)
        & out[TRAIN_X].notna().all(axis=1)
    )
    dropped = int((~ok).sum())
    out = out.loc[ok].drop_duplicates(subset=["run_id", "elapsed_smoking_min"]).reset_index(drop=True)
    print(f"Training clean: dropped {dropped} bad rows, kept {len(out)}")
    return out


def build() -> pd.DataFrame:
    # Build the main catfish dataset (real experimental data at ~3342g)
    catfish_main = build_catfish_main()
    
    # Extract parameters for power law scaling from the real data
    m_main = float(catfish_main.start_weight_g.iloc[0])  # ~3342g
    t_main = float(catfish_main.elapsed_smoking_min.iloc[-1])
    q_main = float(catfish_main.target_oven_deg_h.iloc[-1])
    lf_main = float(catfish_main.target_loss_frac.iloc[-1])
    
    # For synthetic data generation, we create a reference point for 800g
    # This follows the same approach as the shawa fish dataset
    m_ref = 800.0  # Reference small load for synthetic generation
    # Estimate scaling factors based on the real data
    # Time and heat dose scale with mass (using power law)
    t_ref = t_main * (m_ref / m_main) ** 0.8  # Time scales with mass^0.8
    q_ref = q_main * (m_ref / m_main) ** 0.8  # Heat dose scales similarly
    lf_ref = lf_main  # Loss fraction stays relatively constant
    
    # Fit power law parameters using both points
    a_t, k_t = power_law_fit(m_ref, t_ref, m_main, t_main)
    a_q, k_q = power_law_fit(m_ref, q_ref, m_main, q_main)
    a_l, k_l = power_law_fit(m_ref, lf_ref, m_main, lf_main)
    
    print(
        f"scale  time min = {a_t:.4g} * mass^{k_t:.3f}  "
        f"°C·h = {a_q:.4g} * mass^{k_q:.3f}  "
        f"loss_frac = {a_l:.4g} * mass^{k_l:.3f}"
    )

    # Generate synthetic datasets for different load sizes
    synths = []
    for mass in SYNTH_LOADS_G:
        t_new = predict_power(a_t, k_t, mass)
        q_new = predict_power(a_q, k_q, mass)
        lf_new = float(np.clip(predict_power(a_l, k_l, mass), 0.15, 0.40))
        syn = synthesize_from_template(
            catfish_main, mass, t_new, lf_new, run_id=f"catfish_synth_{int(mass)}g"
        )
        # Match heat dose to the two-point fit
        q_scale = q_new / float(syn.target_oven_deg_h.iloc[-1])
        syn["oven_deg_h"] = syn.oven_deg_h * q_scale
        syn = add_targets_and_gates(syn)
        synths.append(syn)
        print(f"  adjusted °C·h target {syn.target_oven_deg_h.iloc[-1]:.0f}")

    # Combine all datasets
    all_runs = pd.concat([catfish_main, *synths], ignore_index=True)
    dataset = all_runs[KEEP].copy()
    dataset.to_csv(OUT_FULL, index=False)
    train = to_training_frame(dataset)
    train.to_csv(OUT_CSV, index=False)
    print(f"Wrote {OUT_FULL}  rows={len(dataset)}")
    print(f"Wrote {OUT_CSV}  training rows={len(train)}  y={TRAIN_Y}")
    print(f"X = {TRAIN_X}")
    print("Split with GroupKFold on run_id; do not put run_id/is_synthetic in X.")
    return train


if __name__ == "__main__":
    build()