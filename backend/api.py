from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import numpy as np
from datetime import datetime

from core.audio_processor import AudioProcessor
from core.feature_extractor import FeatureExtractor
from core.model_manager import ModelManager
from core.alert_system import AlertSystem
from database import DatabaseManager

app = FastAPI(title="Voice Biomarker API", description="AI Disease Tracking Endpoints")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize using the SAME core modules as app.py (Streamlit)
processor = AudioProcessor()
extractor = FeatureExtractor()
model_manager = ModelManager()
alert_system = AlertSystem()

# In-memory session history for alert trend tracking
session_history = []

# Temporary storage for processing
UPLOAD_DIR = "temp_audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def index():
    return {
        "service": "VitaScan Voice Biomarker API",
        "status": "active",
        "model_ready": model_manager.is_ready(),
        "classes": model_manager.classes if model_manager.is_ready() else [],
    }


@app.get("/health")
def health_check():
    return {
        "model_loaded": model_manager.is_ready(),
        "classes": model_manager.classes if model_manager.is_ready() else [],
    }


@app.post("/upload-audio")
async def upload_and_predict(
    file: UploadFile = File(...),
    token: str = Form(None),
    userId: str = Form(None),
):
    """
    Full analysis pipeline matching app.py (Streamlit):
    Audio → AudioProcessor → FeatureExtractor (150-dim) → ModelManager → AlertSystem → Response
    """
    if not model_manager.is_ready():
        raise HTTPException(500, "Model components not loaded. Ensure model.pkl, scaler.pkl, label_encoder.pkl exist.")

    audio_path = os.path.join(UPLOAD_DIR, file.filename or "upload.wav")
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # ── Step 1: Audio Preprocessing (same as app.py) ──
        audio_norm, sr = processor.process(audio_path)

        # ── Step 2: Extract 150-dim features (same as app.py) ──
        features = extractor.extract_all(audio_norm, sr)

        # ── Step 3: Predict using real model (same as app.py) ──
        result = model_manager.predict(features)

        # ── Step 4: Check alerts against session history (same as app.py) ──
        alerts = alert_system.check_alerts(result, session_history)
        result["alerts"] = alerts

        # ── Step 5: Extract diagnostic components for radar chart (same as app.py) ──
        diagnostics = extractor.extract_diagnostic_components(audio_norm, sr)
        result["diagnostics"] = diagnostics

        # ── Step 6: Store in session history for trend tracking ──
        history_entry = {
            "day": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "disease": result["predicted_disease"],
            "probability": result["probability"],
            "risk": result["risk_level"],
            "alerts": result["alerts"],
            "all_probs": result["all_probabilities"],
            "explanation": result["explanation"],
        }
        session_history.append(history_entry)

        # ── Step 7: Save to Firebase Firestore (same as app.py) ──
        user_id = userId or "anonymous"
        user_token = token or None
        try:
            DatabaseManager.save_prediction(
                audio_url="pending_sync",
                prediction=result["predicted_disease"],
                probability=result["probability"] / 100.0,
                risk_level=result["risk_level"],
                user_id=user_id,
                user_token=user_token,
            )
        except Exception as db_err:
            print(f"[API] Firebase save failed (non-critical): {db_err}")

        # ── Return full rich response matching app.py output ──
        return JSONResponse(content={
            "predicted_disease": result["predicted_disease"],
            "probability": result["probability"],
            "all_probabilities": result["all_probabilities"],
            "risk_level": result["risk_level"],
            "explanation": result["explanation"],
            "alerts": result["alerts"],
            "diagnostics": result["diagnostics"],
        })

    except Exception as e:
        print(f"[API] Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Analysis pipeline failed: {str(e)}")

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)


@app.get("/reports")
def get_reports(userId: str = "anonymous", token: str = None):
    """Fetch past reports from Firebase Firestore"""
    reports = DatabaseManager.get_past_reports(user_id=userId, user_token=token)
    return JSONResponse(content=reports)


@app.get("/session-history")
def get_session_history():
    """Returns in-memory session history for progress tracking"""
    return JSONResponse(content=session_history)
