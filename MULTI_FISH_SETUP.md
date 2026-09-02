# Multi-Fish Model Setup Guide

## Overview
This setup enables the intelligent fish smoking system to handle three types of fish:
- **Shawa** (original dataset, ~2500g experimental data)
- **Catfish** (~3342g experimental data) 
- **Tuna** (~2379g experimental data)

## Key Changes

### 1. Dataset Combination
- Combined three separate datasets into one training set
- Added `fish_type` as a categorical feature
- Encoded fish types: shawa=0, catfish=1, tuna=2

### 2. Model Training
- **New script**: `train_multi_fish_model.py`
- **Output**: `multi_fish_remaining_time_model.joblib`
- **Features**: All original features + `fish_type_encoded`
- **Algorithm**: RandomForestRegressor (same as original)
- **Validation**: Leave-one-run-out cross-validation

### 3. Backend Changes (`app.py`)
- **Model Loading**: Prioritizes multi-fish model, falls back to single-fish model
- **Session Start**: Fish type is now **required** (validation enforced)
- **Prediction Logic**: 
  - Only makes predictions when session is running
  - Only uses model when session is active AND valid sensor data available
  - Encodes fish type for multi-fish model predictions
- **No Session**: Logs sensor readings to frontend without model predictions

### 4. Frontend Changes
- **Fish Type Selection**: Required dropdown with options: Shawa, Catfish, Tuna
- **Validation**: Prevents session start without fish type selection
- **Display Logic**: 
  - Shows sensor readings regardless of session status
  - Shows predicted time ONLY when session is running AND prediction is ready
  - Shows "—" for predictions when no session is active

## Training the Model

### Prerequisites
Ensure all three dataset files exist:
- `smoking_remaining_time_dataset.csv` (shawa)
- `catfish_smoking_remaining_time_dataset.csv` (catfish)
- `tuna_smoking_remaining_time_dataset.csv` (tuna)

### Run Training
```bash
python train_multi_fish_model.py
```

### Expected Output
- Combined dataset statistics
- Cross-validation results (MAE, R² for each held-out run)
- Feature importance rankings
- Model saved as `multi_fish_remaining_time_model.joblib`

## Usage Flow

### Starting a Session
1. User opens the web interface
2. User clicks "Start session"
3. User **must select** fish type (Shawa, Catfish, or Tuna)
4. User optionally enters starting weight (or uses load cell)
5. System validates fish type and starts session
6. ESP32 begins sending sensor data
7. Backend processes telemetry + fish type through model
8. Frontend displays predicted remaining time

### No Active Session
1. ESP32 sends sensor data to backend
2. Backend logs sensor readings WITHOUT model processing
3. Frontend displays raw sensor values
4. **Predicted time shows "—"** (blank)
5. System waits for user to start a session

### Session Paused/Stopped
- Predictions stop immediately
- Sensor readings continue to display
- Relay turns OFF (as per original logic)

## File Structure
```
intelligent-fish-smoking-main/
├── train_multi_fish_model.py          # NEW: Training script
├── multi_fish_remaining_time_model.joblib  # NEW: Trained model
├── app.py                               # UPDATED: Backend logic
├── templates/
│   ├── index.html                      # UPDATED: Fish type dropdown
│   └── js/
│       └── app.js                      # UPDATED: Validation & display logic
├── smoking_remaining_time_dataset.csv   # Shawa dataset
├── catfish_smoking_remaining_time_dataset.csv  # Catfish dataset
└── tuna_smoking_remaining_time_dataset.csv     # Tuna dataset
```

## API Changes

### POST /api/session/start
**Before**: `fish_type` was optional
**After**: `fish_type` is **required** (must be: "shawa", "catfish", or "tuna")

**Request Body**:
```json
{
  "fish_type": "shawa",  // Required: "shawa", "catfish", or "tuna"
  "start_weight_g": 2500  // Optional (uses load cell if omitted)
}
```

**Error Response** (if fish type missing/invalid):
```json
{
  "detail": "Fish type is required. Please specify: shawa, catfish, or tuna"
}
```

## Model Features

### Input Features
1. `fish_type_encoded` (0=shawa, 1=catfish, 2=tuna)
2. `start_weight_g` (starting weight in grams)
3. `elapsed_smoking_min` (time elapsed)
4. `oven_temp_c` (oven temperature)
5. `oven_deg_h` (cumulative heat dose)
6. `dht11_temp_c` (ambient temperature)
7. `dht11_humidity_pct` (ambient humidity)
8. `mq6_adc` (gas sensor ADC)
9. `mq6_ratio` (gas sensor ratio)
10. `weight_corrected_g` (corrected weight)
11. `weight_smooth_g` (smoothed weight)
12. `weight_loss_from_start_g` (weight loss)
13. `moisture_removed_frac` (moisture fraction removed)
14. `drying_rate_g_per_min` (drying rate)

### Output
- `remaining_min` (predicted remaining time in minutes)

## Benefits

1. **Robust Model**: Trained on all three fish types for better generalization
2. **Fish Type Awareness**: Model can distinguish between different fish characteristics
3. **User Control**: Users must specify fish type, ensuring accurate predictions
4. **Clean Display**: No predictions shown when not applicable (no session)
5. **Backward Compatible**: Falls back to single-fish model if multi-fish model not available
6. **Live Monitoring**: Sensor readings always displayed regardless of session status

## Troubleshooting

### Model Loading Issues
- Ensure `multi_fish_remaining_time_model.joblib` exists in the project directory
- Check backend logs for model loading errors
- System will fall back to single-fish model if multi-fish model unavailable

### Fish Type Validation
- Ensure fish type matches exactly: "shawa", "catfish", or "tuna" (case-insensitive)
- Check that multi-fish model was trained with all three fish types

### Prediction Issues
- Verify session is in "running" state
- Check that ESP32 is sending valid sensor data
- Ensure fish type was specified when starting session
- Check backend logs for prediction errors

## Next Steps

1. **Train the model**: Run `python train_multi_fish_model.py`
2. **Test the system**: Start sessions with each fish type
3. **Monitor predictions**: Verify accuracy for each fish type
4. **Adjust if needed**: Retrain with more data if predictions are inaccurate