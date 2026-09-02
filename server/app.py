"""FastAPI backend server for intelligent fish smoking.

This server manages the smoking session, accepts sensor data from the ESP32,
runs predictions using the pre-trained Random Forest model, persists cook data
to CSV logs, and sends commands back to the ESP32 to trigger the relay.
"""
from __future__ import annotations

import logging
import sys
import threading
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Deque

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Resolve paths
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
MODEL_PATH = ROOT_DIR / "remaining_time_model.joblib"
LOGS_DIR = BASE_DIR / "session_logs"
LOGS_DIR.mkdir(exist_ok=True)

# Global model container
MODEL_PAYLOAD: Optional[Dict[str, Any]] = None

try:
    if MODEL_PATH.exists():
        logging.info(f"Loading pre-trained model from {MODEL_PATH}...")
        MODEL_PAYLOAD = joblib.load(MODEL_PATH)
        logging.info(f"Model successfully loaded. Features expected: {MODEL_PAYLOAD['features']}")
    else:
        logging.warning(
            f"Model file not found at {MODEL_PATH}. "
            f"Please run 'python train_remaining_time.py' first to generate it."
        )
except Exception as e:
    logging.error(f"Error loading model from {MODEL_PATH}: {e}")


# =====================================================================
# State Manager
# =====================================================================
class SessionStateManager:
    """Manages the in-memory state of the active smoking session."""

    def __init__(self):
        self.lock = threading.Lock()
        self.reset_state()

    def reset_state(self):
        self.session_id: Optional[str] = None
        self.status: str = "idle"  # idle, running, paused, stopped
        self.start_weight_g: float = 0.0
        self.elapsed_smoking_min: float = 0.0
        self.oven_deg_h: float = 0.0
        self.last_reading_time: Optional[datetime] = None
        self.last_prediction_min: float = 0.0
        
        self.history: List[Dict[str, Any]] = []
        self.weight_history: Deque[float] = deque(maxlen=12)
        self.drying_rate_history: Deque[float] = deque(maxlen=24)
        
        self.last_raw_telemetry: Dict[str, Any] = {}
        self.last_weight_smooth: float = 0.0
        self.last_elapsed_min: float = 0.0

    def start_session(self, initial_weight_g: Optional[float] = None) -> str:
        with self.lock:
            # We can start a new session or transition from stopped/idle
            self.reset_state()
            self.session_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.status = "running"
            self.last_reading_time = None
            if initial_weight_g is not None and initial_weight_g > 0.0:
                self.start_weight_g = initial_weight_g
            logging.info(f"Started session {self.session_id} with initial weight: {self.start_weight_g}g")
            return self.session_id

    def pause_session(self):
        with self.lock:
            if self.status == "running":
                self.status = "paused"
                # Clear last reading time to prevent elapsed time jumps on resume
                self.last_reading_time = None
                logging.info(f"Paused session {self.session_id}")

    def resume_session(self):
        with self.lock:
            if self.status == "paused":
                self.status = "running"
                self.last_reading_time = None
                logging.info(f"Resumed session {self.session_id}")

    def stop_session(self):
        with self.lock:
            if self.status in ("running", "paused"):
                self.status = "stopped"
                logging.info(f"Stopped session {self.session_id}")

    def process_telemetry(self, raw_data: Dict[str, float]) -> Dict[str, Any]:
        with self.lock:
            now = datetime.now()
            
            # Extract raw values
            dht_temp = raw_data.get("dht11_temp_c", 0.0)
            dht_hum = raw_data.get("dht11_humidity_pct", 0.0)
            oven_temp = raw_data.get("oven_temp_c", 0.0)
            mq6_adc = raw_data.get("mq6_adc", 0.0)
            mq6_ratio = raw_data.get("mq6_ratio", 0.0)
            weight_raw = raw_data.get("weight_g", 0.0)

            # Keep last telemetry reading
            self.last_raw_telemetry = {
                "timestamp": now.isoformat(),
                "dht11_temp_c": dht_temp,
                "dht11_humidity_pct": dht_hum,
                "oven_temp_c": oven_temp,
                "mq6_adc": mq6_adc,
                "mq6_ratio": mq6_ratio,
                "weight_g": weight_raw,
            }

            # Return quickly if session is not active/running
            if self.status != "running":
                return {
                    "session_id": self.session_id,
                    "session_state": self.status,
                    "relay_state": "ON" if self.status == "running" else "OFF",
                    "elapsed_smoking_min": self.elapsed_smoking_min,
                    "predicted_remaining_min": self.last_prediction_min,
                    "start_weight_g": self.start_weight_g,
                    "latest_telemetry": self.last_raw_telemetry,
                }

            # 1. Handle auto-capture of starting weight if not set manually
            if self.start_weight_g <= 0.0 and weight_raw > 10.0:
                self.start_weight_g = weight_raw

            # 2. Compute dt_s (time difference since last packet)
            dt_s = 0.0
            if self.last_reading_time is not None:
                dt_s = (now - self.last_reading_time).total_seconds()
                if dt_s < 0.0:
                    dt_s = 0.0
                elif dt_s > 60.0:
                    # Cap dt_s to avoid massive spikes if ESP32 went offline temporarily
                    dt_s = 10.0  # assume typical 10s fallback interval
            else:
                # First reading in running session
                dt_s = 0.0

            self.last_reading_time = now

            # 3. Increment elapsed smoking time (only when running)
            self.elapsed_smoking_min += dt_s / 60.0

            # 4. Compute cumulative oven degree hours
            self.oven_deg_h += oven_temp * (dt_s / 3600.0)

            # 5. Outlier/dropout correction for weight
            weight_corrected = weight_raw
            if len(self.weight_history) > 0:
                last_valid = self.weight_history[-1]
                # If weight drops to a tiny value suddenly, treat it as a temporary dropout
                if weight_raw < last_valid * 0.2 and last_valid > 100.0:
                    weight_corrected = last_valid
            
            self.weight_history.append(weight_corrected)

            # 6. Smooth weight (Rolling median of last 12 readings)
            weight_smooth = float(np.median(list(self.weight_history)))

            # 7. Weight loss calculation
            weight_loss = max(0.0, self.start_weight_g - weight_corrected)

            # 8. Moisture removed fraction
            moisture_frac = 0.0
            if self.start_weight_g > 0.0:
                moisture_frac = weight_loss / self.start_weight_g

            # 9. Real-time drying rate (g/min) estimation
            # matches: rolling(24, min_periods=4).median() of diffs
            drying_rate = 0.0
            time_diff = self.elapsed_smoking_min - self.last_elapsed_min
            if time_diff > 0.001:
                weight_diff = weight_smooth - self.last_weight_smooth
                instant_rate = weight_diff / time_diff
                self.drying_rate_history.append(instant_rate)

            if len(self.drying_rate_history) >= 4:
                drying_rate = float(np.median(list(self.drying_rate_history)))
            else:
                drying_rate = 0.0

            # Update cache variables
            self.last_elapsed_min = self.elapsed_smoking_min
            self.last_weight_smooth = weight_smooth

            # 10. Compile feature dictionary matching model's expected features
            features_dict = {
                "start_weight_g": self.start_weight_g,
                "elapsed_smoking_min": self.elapsed_smoking_min,
                "oven_temp_c": oven_temp,
                "oven_deg_h": self.oven_deg_h,
                "dht11_temp_c": dht_temp,
                "dht11_humidity_pct": dht_hum,
                "mq6_adc": mq6_adc,
                "mq6_ratio": mq6_ratio,
                "weight_corrected_g": weight_corrected,
                "weight_smooth_g": weight_smooth,
                "weight_loss_from_start_g": weight_loss,
                "moisture_removed_frac": moisture_frac,
                "drying_rate_g_per_min": drying_rate,
            }

            # 11. Run prediction using the random forest model
            predicted_remaining_min = 0.0
            if MODEL_PAYLOAD is not None:
                try:
                    model = MODEL_PAYLOAD["model"]
                    features_list = MODEL_PAYLOAD["features"]

                    # Construct exact DataFrame input format
                    df_input = pd.DataFrame([features_dict], columns=features_list)
                    predicted_remaining_min = float(model.predict(df_input)[0])
                    # Ensure prediction is sensible and non-negative
                    predicted_remaining_min = max(0.0, predicted_remaining_min)
                except Exception as e:
                    logging.error(f"Prediction failed: {e}")
                    predicted_remaining_min = self.last_prediction_min
            else:
                # Basic rule-based fallback if model is not loaded:
                # Estimate remaining time based on remaining weight target loss of 25%
                target_loss_frac = 0.25
                if drying_rate < -0.05:
                    target_loss_g = self.start_weight_g * target_loss_frac
                    leftover_loss_g = max(0.0, target_loss_g - weight_loss)
                    predicted_remaining_min = leftover_loss_g / abs(drying_rate)
                else:
                    predicted_remaining_min = 180.0  # default dummy fallback

            self.last_prediction_min = predicted_remaining_min

            # Compile record for history and CSV logging
            record = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "elapsed_smoking_min": self.elapsed_smoking_min,
                "predicted_remaining_min": predicted_remaining_min,
                **features_dict,
            }
            self.history.append(record)

            return {
                "status": "success",
                "session_id": self.session_id,
                "session_state": self.status,
                "relay_state": "ON" if self.status == "running" else "OFF",
                "elapsed_smoking_min": self.elapsed_smoking_min,
                "predicted_remaining_min": predicted_remaining_min,
                "calculated_features": features_dict,
                "latest_telemetry": self.last_raw_telemetry,
                "record": record,
            }


# =====================================================================
# App Setup & CORS
# =====================================================================
app = FastAPI(
    title="Intelligent Fish Smoking Backend API",
    description="Backend API for ESP32 and frontend integration, with ML remaining time prediction.",
    version="1.0.0",
)

# Configure CORS to allow frontend communication from any origin (e.g. Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_manager = SessionStateManager()


# =====================================================================
# Connection Manager for WebSockets (Real-time Frontend Push)
# =====================================================================
class ConnectionManager:
    """Manages active WebSocket connections for push updates to the frontend."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logging.info(f"WebSocket client connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logging.info(f"WebSocket client disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Silently handle dead connection and discard
                pass


ws_manager = ConnectionManager()


# =====================================================================
# Background Tasks (CSV Logging)
# =====================================================================
def save_log_task(session_id: str, record: Dict[str, Any]):
    """Appends the newest cook record to the session CSV file asynchronously."""
    try:
        csv_path = LOGS_DIR / f"session_{session_id}.csv"
        df = pd.DataFrame([record])
        if not csv_path.exists():
            df.to_csv(csv_path, index=False)
        else:
            df.to_csv(csv_path, mode="a", header=False, index=False)
    except Exception as e:
        logging.error(f"Failed to save record to CSV: {e}")


# =====================================================================
# Request/Response Schemas
# =====================================================================
class StartRequest(BaseModel):
    start_weight_g: Optional[float] = Field(
        None, description="Starting weight of fish. If omitted, first load cell reading is used."
    )


class SessionStatusResponse(BaseModel):
    session_id: Optional[str]
    session_state: str
    relay_state: str
    start_weight_g: float
    elapsed_smoking_min: float
    predicted_remaining_min: float
    latest_telemetry: Dict[str, Any]


# =====================================================================
# REST Endpoints
# =====================================================================
@app.get("/")
async def root():
    return {
        "app": "Intelligent Fish Smoking Backend",
        "api_docs": "/docs",
        "status": "online",
        "model_loaded": MODEL_PAYLOAD is not None,
    }


@app.get("/api/status", response_model=SessionStatusResponse)
async def get_status():
    """Returns the current session status and latest telemetry."""
    return {
        "session_id": session_manager.session_id,
        "session_state": session_manager.status,
        "relay_state": "ON" if session_manager.status == "running" else "OFF",
        "start_weight_g": session_manager.start_weight_g,
        "elapsed_smoking_min": session_manager.elapsed_smoking_min,
        "predicted_remaining_min": session_manager.last_prediction_min,
        "latest_telemetry": session_manager.last_raw_telemetry,
    }


@app.post("/api/session/start")
async def start_session(body: Optional[StartRequest] = None):
    """Starts a new smoking session."""
    initial_weight = body.start_weight_g if body else None
    session_id = session_manager.start_session(initial_weight)
    
    # Broadcast state change to WebSocket clients
    status_data = {
        "event": "state_change",
        "session_id": session_id,
        "session_state": "running",
        "relay_state": "ON",
    }
    await ws_manager.broadcast(status_data)
    
    return {"status": "success", "session_id": session_id, "message": "Session started."}


@app.post("/api/session/pause")
async def pause_session():
    """Pauses the active smoking session (freezes timers, relay goes OFF)."""
    session_manager.pause_session()
    
    # Broadcast state change
    status_data = {
        "event": "state_change",
        "session_id": session_manager.session_id,
        "session_state": "paused",
        "relay_state": "OFF",
    }
    await ws_manager.broadcast(status_data)
    
    return {"status": "success", "message": "Session paused."}


@app.post("/api/session/resume")
async def resume_session():
    """Resumes a paused smoking session (re-activates timers, relay goes ON)."""
    if session_manager.status != "paused":
        raise HTTPException(status_code=400, detail="Session is not paused.")
    session_manager.resume_session()
    
    # Broadcast state change
    status_data = {
        "event": "state_change",
        "session_id": session_manager.session_id,
        "session_state": "running",
        "relay_state": "ON",
    }
    await ws_manager.broadcast(status_data)
    
    return {"status": "success", "message": "Session resumed."}


@app.post("/api/session/stop")
async def stop_session():
    """Stops the current smoking session (relay goes OFF)."""
    session_manager.stop_session()
    
    # Broadcast state change
    status_data = {
        "event": "state_change",
        "session_id": session_manager.session_id,
        "session_state": "stopped",
        "relay_state": "OFF",
    }
    await ws_manager.broadcast(status_data)
    
    return {"status": "success", "message": "Session stopped."}


@app.post("/api/session/reset")
async def reset_session():
    """Resets the system back to the idle state, clearing historical data."""
    session_manager.reset_state()
    
    # Broadcast state change
    status_data = {
        "event": "state_change",
        "session_id": None,
        "session_state": "idle",
        "relay_state": "OFF",
    }
    await ws_manager.broadcast(status_data)
    
    return {"status": "success", "message": "Session state reset."}


@app.get("/api/session/history")
async def get_history():
    """Returns the time-series logs of the active session (perfect for UI charts)."""
    return {
        "session_id": session_manager.session_id,
        "session_state": session_manager.status,
        "history_len": len(session_manager.history),
        "history": session_manager.history,
    }


@app.post("/api/telemetry")
async def receive_telemetry(payload: Dict[str, Any], background_tasks: BackgroundTasks):
    """Receives live sensor telemetry from the ESP32.

    Processes values, runs ML predictions if a session is running, writes log entries,
    and returns instructions (such as the relay command) back to the ESP32.
    """
    # Keys normalization mapping to support different naming formats (DHT11_Temp_C, Weight_g etc.)
    mappings = {
        "dht11_temp_c": ["dht11_temp_c", "DHT11_Temp_C", "dht11_temp"],
        "dht11_humidity_pct": ["dht11_humidity_pct", "DHT11_Humidity_pct", "dht11_humidity"],
        "oven_temp_c": ["oven_temp_c", "MAX6675_OvenTemp_C", "oven_temp", "MAX6675_OvenTemp"],
        "mq6_adc": ["mq6_adc", "MQ6_ADC", "mq6"],
        "mq6_ratio": ["mq6_ratio", "MQ6_Ratio", "mq6_rat"],
        "weight_g": ["weight_g", "Weight_g", "weight"],
    }
    
    normalized_data = {}
    for target_key, aliases in mappings.items():
        found_val = None
        for alias in aliases:
            if alias in payload:
                found_val = payload[alias]
                break
        normalized_data[target_key] = float(found_val) if found_val is not None else 0.0

    # Process and compute model variables
    result = session_manager.process_telemetry(normalized_data)
    
    # Broadcast live update to any frontend listening via WebSockets
    if ws_manager.active_connections:
        ws_payload = {
            "event": "telemetry_update",
            "session_id": session_manager.session_id,
            "session_state": session_manager.status,
            "relay_state": result["relay_state"],
            "elapsed_smoking_min": result["elapsed_smoking_min"],
            "predicted_remaining_min": result["predicted_remaining_min"],
            "latest_telemetry": result["latest_telemetry"],
        }
        if "calculated_features" in result:
            ws_payload["calculated_features"] = result["calculated_features"]
        background_tasks.add_task(ws_manager.broadcast, ws_payload)

    # If session is running, save record to CSV file asynchronously
    if session_manager.status == "running" and session_manager.session_id and "record" in result:
        background_tasks.add_task(save_log_task, session_manager.session_id, result["record"])

    # Returns instructions to the ESP32 (including the relay state).
    # FIXED: Included additional keys required by the simulation_tick endpoint!
    return {
        "status": "success",
        "session_id": result.get("session_id"),
        "session_state": result["session_state"],
        "relay_state": result["relay_state"],
        "elapsed_smoking_min": result.get("elapsed_smoking_min", 0.0),
        "predicted_remaining_min": result.get("predicted_remaining_min", 0.0),
    }


@app.get("/api/relay")
async def get_relay():
    """Independent endpoint for the ESP32 to poll only for the current relay status."""
    return {
        "relay_state": "ON" if session_manager.status == "running" else "OFF"
    }


# =====================================================================
# Simulation Tool (Extremely useful for frontend offline testing)
# =====================================================================
@app.post("/api/simulation/tick")
async def simulation_tick(background_tasks: BackgroundTasks):
    """Generates a mock telemetry tick for testing the frontend and model flow offline.

    Increments time, decreases weight, adjusts temperatures, and triggers model predictions.
    """
    if session_manager.status != "running":
        raise HTTPException(status_code=400, detail="Simulation requires an active running session.")

    # Calculate some realistic mock data based on how long we have smoked
    elapsed = session_manager.elapsed_smoking_min
    start_w = session_manager.start_weight_g if session_manager.start_weight_g > 0 else 1200.0
    
    # Weight decreases linearly + noise
    weight_loss = min(start_w * 0.3, elapsed * 2.5)  # lose up to 30% weight
    mock_weight = max(100.0, start_w - weight_loss + np.random.normal(0, 0.5))
    
    # Oven heats up to 100°C, then fluctuates
    mock_oven = min(110.0, 30.0 + elapsed * 8.0) + np.random.normal(0, 1.0)
    
    # Smoke ratio increases as smoke builds up, then stabilizes
    mock_mq6 = min(800.0, 200.0 + elapsed * 15.0) + np.random.normal(0, 5.0)
    mock_ratio = min(15.0, 1.0 + elapsed * 0.1) + np.random.normal(0, 0.05)
    
    # Room humidity drops, room temperature rises slightly
    mock_dht_temp = 25.0 + min(10.0, elapsed * 0.2) + np.random.normal(0, 0.1)
    mock_dht_hum = max(35.0, 65.0 - elapsed * 0.4) + np.random.normal(0, 0.2)

    mock_payload = {
        "dht11_temp_c": mock_dht_temp,
        "dht11_humidity_pct": mock_dht_hum,
        "oven_temp_c": mock_oven,
        "mq6_adc": mock_mq6,
        "mq6_ratio": mock_ratio,
        "weight_g": mock_weight,
    }

    # Process normalized data as if received from ESP32
    result = await receive_telemetry(mock_payload, background_tasks)
    
    return {
        "status": "success",
        "simulated_values": mock_payload,
        "processed_result": {
            "session_id": result["session_id"],
            "session_state": result["session_state"],
            "relay_state": result["relay_state"],
            "elapsed_smoking_min": result["elapsed_smoking_min"],
            "predicted_remaining_min": result["predicted_remaining_min"],
        }
    }


# =====================================================================
# WebSocket Handler
# =====================================================================
@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Establishes a persistent full-duplex connection with the frontend."""
    await ws_manager.connect(websocket)
    try:
        # Push initial status upon connection
        await websocket.send_json({
            "event": "connection_established",
            "session_id": session_manager.session_id,
            "session_state": session_manager.status,
            "relay_state": "ON" if session_manager.status == "running" else "OFF",
            "start_weight_g": session_manager.start_weight_g,
            "elapsed_smoking_min": session_manager.elapsed_smoking_min,
            "predicted_remaining_min": session_manager.last_prediction_min,
            "latest_telemetry": session_manager.last_raw_telemetry,
        })
        
        while True:
            # Maintain connection, handle any client messages if sent (mostly heartbeats)
            data = await websocket.receive_text()
            await websocket.send_json({"event": "pong", "data": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


# =====================================================================
# Run Server Instructions (fallback if executed directly)
# =====================================================================
if __name__ == "__main__":
    import uvicorn
    # Automatically starts uvicorn on port 8000 when main.py is executed directly
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
