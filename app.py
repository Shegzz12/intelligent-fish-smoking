"""FastAPI server for intelligent fish smoking — API + Smokehouse dashboard.

The dashboard is served from templates/ at the same origin as the API.
Relay stays ON while a session is running until pause / stop / reset.
"""
from __future__ import annotations

import logging
import os
import sys
import threading
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import BackgroundTasks, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
TEMPLATES_DIR = BASE_DIR / "templates"

# ---------------------------------------------------------------------------
# Portable model path resolution.
#
# Works identically on Windows dev machines and on Render's Linux containers
# because it never hardcodes an absolute path — it only ever looks relative
# to this file (BASE_DIR) or its parent (ROOT_DIR), with an optional env var
# escape hatch if you ever want to point at a model stored outside the repo
# (e.g. mounted on a Render persistent disk) without a redeploy.
# ---------------------------------------------------------------------------
_env_override = os.environ.get("MODEL_PATH")

_MODEL_CANDIDATES = [
    Path(_env_override) if _env_override else None,
    BASE_DIR / "multi_fish_remaining_time_model.joblib",
    ROOT_DIR / "multi_fish_remaining_time_model.joblib",
    ROOT_DIR / "remaining_time_model.joblib",
    BASE_DIR / "remaining_time_model.joblib",
]
_MODEL_CANDIDATES = [p for p in _MODEL_CANDIDATES if p is not None]

MODEL_PATH = next((p for p in _MODEL_CANDIDATES if p.exists()), _MODEL_CANDIDATES[0])

LOGS_DIR = BASE_DIR / "session_logs"
LOGS_DIR.mkdir(exist_ok=True)

MODEL_PAYLOAD: Optional[Dict[str, Any]] = None

try:
    if MODEL_PATH.exists():
        logging.info("Loading pre-trained model from %s...", MODEL_PATH)
        MODEL_PAYLOAD = joblib.load(MODEL_PATH)
        model_type = MODEL_PAYLOAD.get("model_type", "single_fish")
        logging.info("Model loaded. Type: %s, Features expected: %s",
                    model_type, MODEL_PAYLOAD["features"])
        if model_type == "multi_fish":
            logging.info("Multi-fish model loaded. Fish types: %s",
                        MODEL_PAYLOAD.get("fish_type_classes", []))
    else:
        logging.warning(
            "Model file not found. Checked: %s. Run train_multi_fish_model.py to generate it, "
            "or set the MODEL_PATH env var to point at it.",
            ", ".join(str(p) for p in _MODEL_CANDIDATES),
        )
except Exception as e:
    logging.error("Error loading model from %s: %s", MODEL_PATH, e)


class SessionStateManager:
    """In-memory smoking session. Relay stays ON while status is running."""

    def __init__(self):
        self.lock = threading.Lock()
        self.completed_sessions: List[Dict[str, Any]] = []
        self.reset_state()

    def reset_state(self):
        self.session_id: Optional[str] = None
        self.status: str = "idle"
        self.fish_type: Optional[str] = None
        self.start_weight_g: float = 0.0
        self.elapsed_smoking_min: float = 0.0
        self.oven_deg_h: float = 0.0
        self.last_reading_time: Optional[datetime] = None
        self.last_prediction_min: Optional[float] = None
        self.prediction_ready: bool = False
        self.history: List[Dict[str, Any]] = []
        self.weight_history: Deque[float] = deque(maxlen=12)
        self.drying_rate_history: Deque[float] = deque(maxlen=24)
        self.last_raw_telemetry: Dict[str, Any] = {}
        self.last_weight_smooth: float = 0.0
        self.last_elapsed_min: float = 0.0

    def snapshot(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "session_id": self.session_id,
                "session_state": self.status,
                "relay_state": "ON" if self.status == "running" else "OFF",
                "fish_type": self.fish_type,
                "start_weight_g": self.start_weight_g,
                "elapsed_smoking_min": self.elapsed_smoking_min,
                "predicted_remaining_min": self.last_prediction_min if self.prediction_ready else None,
                "prediction_ready": self.prediction_ready,
                "model_loaded": MODEL_PAYLOAD is not None,
                "latest_telemetry": dict(self.last_raw_telemetry),
            }

    def start_session(
        self,
        initial_weight_g: Optional[float] = None,
        fish_type: Optional[str] = None,
    ) -> str:
        with self.lock:
            self.reset_state()
            self.session_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.status = "running"

            # Fish type is now required for multi-fish model
            fish_type_clean = (fish_type or "").strip().lower()
            if not fish_type_clean:
                raise ValueError("Fish type is required. Please specify: shawa, catfish, or tuna")

            # Validate fish type against model if multi-fish model is loaded
            if MODEL_PAYLOAD and MODEL_PAYLOAD.get("model_type") == "multi_fish":
                valid_types = MODEL_PAYLOAD.get("fish_type_classes", [])
                if fish_type_clean not in [t.lower() for t in valid_types]:
                    raise ValueError(f"Invalid fish type. Must be one of: {valid_types}")

            self.fish_type = fish_type_clean
            self.last_reading_time = None
            if initial_weight_g is not None and initial_weight_g > 0.0:
                self.start_weight_g = initial_weight_g
            logging.info(
                "Started session %s (relay ON) fish=%s weight=%sg",
                self.session_id,
                self.fish_type,
                self.start_weight_g,
            )
            return self.session_id

    def pause_session(self):
        with self.lock:
            if self.status == "running":
                self.status = "paused"
                self.last_reading_time = None
                logging.info("Paused session %s (relay OFF)", self.session_id)

    def resume_session(self):
        with self.lock:
            if self.status == "paused":
                self.status = "running"
                self.last_reading_time = None
                logging.info("Resumed session %s (relay ON)", self.session_id)

    def stop_session(self):
        with self.lock:
            if self.status in ("running", "paused"):
                self.completed_sessions.insert(
                    0,
                    {
                        "session_id": self.session_id,
                        "fish_type": self.fish_type,
                        "start_weight_g": self.start_weight_g,
                        "elapsed_smoking_min": self.elapsed_smoking_min,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "result": "Stopped",
                    },
                )
                self.status = "stopped"
                logging.info("Stopped session %s (relay OFF)", self.session_id)

    def reset_session(self):
        with self.lock:
            logging.info("Reset session %s", self.session_id)
            self.reset_state()

    def process_telemetry(self, raw_data: Dict[str, float]) -> Dict[str, Any]:
        with self.lock:
            now = datetime.now()

            dht_temp = raw_data.get("dht11_temp_c", 0.0)
            dht_hum = raw_data.get("dht11_humidity_pct", 0.0)
            oven_temp = raw_data.get("oven_temp_c", 0.0)
            mq6_adc = raw_data.get("mq6_adc", 0.0)
            mq6_ratio = raw_data.get("mq6_ratio", 0.0)
            weight_raw = raw_data.get("weight_g", 0.0)

            self.last_raw_telemetry = {
                "timestamp": now.isoformat(),
                "dht11_temp_c": dht_temp,
                "dht11_humidity_pct": dht_hum,
                "oven_temp_c": oven_temp,
                "mq6_adc": mq6_adc,
                "mq6_ratio": mq6_ratio,
                "weight_g": weight_raw,
            }

            # Validate that we have meaningful sensor data before making predictions
            # This prevents using zero/invalid values when ESP32 is not connected
            has_valid_sensors = (
                oven_temp > 0.0 and  # Oven temperature should be positive when running
                weight_raw > 0.0 and  # Weight should be positive when fish is loaded
                (dht_temp > 0.0 or dht_hum > 0.0)  # At least one DHT11 reading should be valid
            )

            if self.status != "running":
                return {
                    "session_id": self.session_id,
                    "session_state": self.status,
                    "relay_state": "ON" if self.status == "running" else "OFF",
                    "fish_type": self.fish_type,
                    "elapsed_smoking_min": self.elapsed_smoking_min,
                    "predicted_remaining_min": self.last_prediction_min if self.prediction_ready else None,
                    "prediction_ready": self.prediction_ready,
                    "start_weight_g": self.start_weight_g,
                    "latest_telemetry": self.last_raw_telemetry,
                }

            if self.start_weight_g <= 0.0 and weight_raw > 10.0:
                self.start_weight_g = weight_raw

            dt_s = 0.0
            if self.last_reading_time is not None:
                dt_s = (now - self.last_reading_time).total_seconds()
                if dt_s < 0.0:
                    dt_s = 0.0
                elif dt_s > 60.0:
                    dt_s = 10.0
            self.last_reading_time = now

            self.elapsed_smoking_min += dt_s / 60.0
            self.oven_deg_h += oven_temp * (dt_s / 3600.0)

            weight_corrected = weight_raw
            if len(self.weight_history) > 0:
                last_valid = self.weight_history[-1]
                if weight_raw < last_valid * 0.2 and last_valid > 100.0:
                    weight_corrected = last_valid
            self.weight_history.append(weight_corrected)

            weight_smooth = float(np.median(list(self.weight_history)))
            weight_loss = max(0.0, self.start_weight_g - weight_corrected)

            moisture_frac = 0.0
            if self.start_weight_g > 0.0:
                moisture_frac = weight_loss / self.start_weight_g

            drying_rate = 0.0
            time_diff = self.elapsed_smoking_min - self.last_elapsed_min
            if time_diff > 0.001:
                weight_diff = weight_smooth - self.last_weight_smooth
                self.drying_rate_history.append(weight_diff / time_diff)

            if len(self.drying_rate_history) >= 4:
                drying_rate = float(np.median(list(self.drying_rate_history)))

            self.last_elapsed_min = self.elapsed_smoking_min
            self.last_weight_smooth = weight_smooth

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
                "fish_type": self.fish_type,
            }

            predicted_remaining_min = self.last_prediction_min

            # Only make predictions when:
            # 1. Session is running
            # 2. Model is loaded
            # 3. We have valid sensor data from actual hardware
            # 4. Fish type is specified (for multi-fish model)
            if self.status == "running" and MODEL_PAYLOAD is not None and has_valid_sensors:
                try:
                    model = MODEL_PAYLOAD["model"]
                    features_list = MODEL_PAYLOAD["features"]

                    # Handle fish type encoding for multi-fish model
                    predict_row = {}
                    for key in features_list:
                        if key == "fish_type_encoded":
                            # Encode fish type for multi-fish model
                            if MODEL_PAYLOAD.get("model_type") == "multi_fish":
                                encoder = MODEL_PAYLOAD["fish_type_encoder"]
                                if self.fish_type:
                                    predict_row[key] = int(encoder.transform([self.fish_type])[0])
                                else:
                                    predict_row[key] = 0  # Default encoding
                            else:
                                predict_row[key] = 0  # Not used for single-fish model
                        else:
                            predict_row[key] = features_dict.get(key, 0.0)

                    df_input = pd.DataFrame([predict_row], columns=features_list)
                    predicted_remaining_min = max(0.0, float(model.predict(df_input)[0]))
                    self.prediction_ready = True
                    self.last_prediction_min = predicted_remaining_min
                    logging.info(
                        "Model remaining time: %.2f min (%.0f hrs %.0f mins) - Fish: %s",
                        predicted_remaining_min,
                        predicted_remaining_min // 60.0,
                        predicted_remaining_min % 60.0,
                        self.fish_type or "unknown",
                    )
                except Exception as e:
                    logging.error("Prediction failed: %s", e)
                    self.prediction_ready = False
            else:
                # No prediction when session is not running or conditions not met
                self.prediction_ready = False
                if self.status != "running":
                    logging.debug("No prediction: session not running")
                elif not has_valid_sensors:
                    logging.info("Waiting for valid sensor data before making predictions")
                elif MODEL_PAYLOAD is None:
                    logging.warning("No model loaded; remaining time will stay hidden until a model is available.")
                elif not self.fish_type and MODEL_PAYLOAD.get("model_type") == "multi_fish":
                    logging.warning("Fish type not specified for multi-fish model")

            if not self.prediction_ready:
                predicted_remaining_min = None

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
                "relay_state": "ON",
                "fish_type": self.fish_type,
                "elapsed_smoking_min": self.elapsed_smoking_min,
                "predicted_remaining_min": predicted_remaining_min,
                "prediction_ready": self.prediction_ready,
                "calculated_features": features_dict,
                "latest_telemetry": self.last_raw_telemetry,
                "record": record,
            }


app = FastAPI(
    title="Intelligent Fish Smoking",
    description="Backend API + Smokehouse dashboard for ESP32 fish smoking.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_manager = SessionStateManager()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logging.info("WebSocket client connected. Active: %s", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logging.info("WebSocket client disconnected. Active: %s", len(self.active_connections))

    async def broadcast(self, message: dict):
        dead: List[WebSocket] = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for connection in dead:
            self.disconnect(connection)


ws_manager = ConnectionManager()


def save_log_task(session_id: str, record: Dict[str, Any]):
    try:
        csv_path = LOGS_DIR / f"session_{session_id}.csv"
        df = pd.DataFrame([record])
        if not csv_path.exists():
            df.to_csv(csv_path, index=False)
        else:
            df.to_csv(csv_path, mode="a", header=False, index=False)
    except Exception as e:
        logging.error("Failed to save record to CSV: %s", e)


async def broadcast_state(event: str = "state_change"):
    snap = session_manager.snapshot()
    snap["event"] = event
    await ws_manager.broadcast(snap)


class StartRequest(BaseModel):
    start_weight_g: Optional[float] = Field(
        None, description="Starting weight of fish. If omitted, first load cell reading is used."
    )
    fish_type: str = Field(
        ..., description="Required fish type: 'shawa', 'catfish', or 'tuna'"
    )


class SessionStatusResponse(BaseModel):
    session_id: Optional[str]
    session_state: str
    relay_state: str
    fish_type: Optional[str] = None
    start_weight_g: float
    elapsed_smoking_min: float
    predicted_remaining_min: Optional[float] = None
    prediction_ready: bool = False
    model_loaded: bool = False
    latest_telemetry: Dict[str, Any]


@app.get("/")
async def frontend():
    return FileResponse(TEMPLATES_DIR / "index.html")


@app.get("/api/health")
@app.get("/api")
async def health():
    return {
        "app": "Intelligent Fish Smoking",
        "api_docs": "/docs",
        "status": "online",
        "model_loaded": MODEL_PAYLOAD is not None,
        "model_path": str(MODEL_PATH),
    }


@app.get("/api/status", response_model=SessionStatusResponse)
async def get_status():
    return session_manager.snapshot()


@app.post("/api/session/start")
async def start_session(body: Optional[StartRequest] = None):
    initial_weight = body.start_weight_g if body else None
    fish_type = body.fish_type if body else None
    try:
        session_id = session_manager.start_session(initial_weight, fish_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    await broadcast_state()
    snap = session_manager.snapshot()
    return {
        "status": "success",
        "session_id": session_id,
        "session_state": snap["session_state"],
        "relay_state": snap["relay_state"],
        "message": "Session started. Relay latched ON until pause/stop/reset.",
    }


@app.post("/api/session/pause")
async def pause_session():
    session_manager.pause_session()
    await broadcast_state()
    return {"status": "success", "message": "Session paused.", **session_manager.snapshot()}


@app.post("/api/session/resume")
async def resume_session():
    if session_manager.status != "paused":
        raise HTTPException(status_code=400, detail="Session is not paused.")
    session_manager.resume_session()
    await broadcast_state()
    return {"status": "success", "message": "Session resumed.", **session_manager.snapshot()}


@app.post("/api/session/stop")
async def stop_session():
    session_manager.stop_session()
    await broadcast_state()
    return {"status": "success", "message": "Session stopped. Relay OFF.", **session_manager.snapshot()}


@app.post("/api/session/reset")
async def reset_session():
    session_manager.reset_session()
    await broadcast_state()
    return {"status": "success", "message": "Session state reset.", **session_manager.snapshot()}


@app.get("/api/session/history")
async def get_history():
    with session_manager.lock:
        return {
            "session_id": session_manager.session_id,
            "session_state": session_manager.status,
            "fish_type": session_manager.fish_type,
            "history_len": len(session_manager.history),
            "history": list(session_manager.history),
            "sessions": list(session_manager.completed_sessions),
        }


@app.post("/api/telemetry")
async def receive_telemetry(payload: Dict[str, Any], background_tasks: BackgroundTasks):
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

    result = session_manager.process_telemetry(normalized_data)

    if ws_manager.active_connections:
        ws_payload = {
            "event": "telemetry_update",
            "session_id": result.get("session_id"),
            "session_state": result["session_state"],
            "relay_state": result["relay_state"],
            "fish_type": result.get("fish_type"),
            "elapsed_smoking_min": result["elapsed_smoking_min"],
            "predicted_remaining_min": result["predicted_remaining_min"],
            "prediction_ready": result.get("prediction_ready", False),
            "latest_telemetry": result["latest_telemetry"],
        }
        if "calculated_features" in result:
            ws_payload["calculated_features"] = result["calculated_features"]
        background_tasks.add_task(ws_manager.broadcast, ws_payload)

    if session_manager.status == "running" and session_manager.session_id and "record" in result:
        background_tasks.add_task(save_log_task, session_manager.session_id, result["record"])

    return {
        "status": "success",
        "session_id": result.get("session_id"),
        "session_state": result["session_state"],
        "relay_state": result["relay_state"],
        "elapsed_smoking_min": result.get("elapsed_smoking_min", 0.0),
        "predicted_remaining_min": result.get("predicted_remaining_min"),
        "prediction_ready": result.get("prediction_ready", False),
    }


@app.get("/api/relay")
async def get_relay():
    return {"relay_state": "ON" if session_manager.status == "running" else "OFF"}


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        await websocket.send_json({"event": "connection_established", **session_manager.snapshot()})
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"event": "pong", "data": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logging.error("WebSocket error: %s", e)
        ws_manager.disconnect(websocket)


app.mount("/css", StaticFiles(directory=TEMPLATES_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=TEMPLATES_DIR / "js"), name="js")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)
    