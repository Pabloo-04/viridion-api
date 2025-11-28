import pickle
import numpy as np
from pathlib import Path
from typing import Dict
from app.config import settings


class GardenPredictor:
    """XGBoost / ML model for watering decision (3-feature classifier)"""

    FEATURES = ["Soil Moisture", "Soil Humidity", "Temperature"]

    def __init__(self, model_path: str = "app/models/xgb_watering_model.pkl"):
        self.model_path = model_path or settings.model_path
        self.model = None
        self._load_model()

    # ------------------------------------------------------------------
    # Load Model Safely (no crash if missing or corrupt)
    # ------------------------------------------------------------------
    def _load_model(self):
        file = Path(self.model_path)

        print("\n──────────────────────────────────────────────────────────")
        print(f"🔍 Checking for model at → {file.resolve()}")
        print("──────────────────────────────────────────────────────────")

        if not file.exists():
            print("⚠ Model not found — fallback rules ENABLED")
            self.model = None
            return

        try:
            with open(file, "rb") as f:
                self.model = pickle.load(f)

            print(f"🔥 Model loaded successfully → {self.model_path}")
            print(f"📦 Using features → {self.FEATURES}")

        except Exception as e:
            print(f"❌ Failed to load model → fallback active\n{e}")
            self.model = None

    # ------------------------------------------------------------------
    # Predict from 3 features
    # ------------------------------------------------------------------
    def predict(self, soil_moisture: float, soil_humidity: float, temperature: float) -> Dict:

        # ========= ML Prediction =========
        if self.model:
            try:
                X = np.array([[soil_moisture, soil_humidity, temperature]])
                pred = self.model.predict(X)[0]
                conf = self.model.predict_proba(X)[0].max()

                return {
                    "should_water": bool(pred),
                    "confidence": round(float(conf), 3),
                    "method": "xgboost_model"
                }
            except Exception as e:
                print(f"⚠ Model prediction failed → {e}")

        # ========= FALLBACK =============
        if soil_moisture < 30 or soil_humidity < 35:
            return {
                "should_water": True,
                "confidence": 0.70,
                "method": "rule-based (dry soil)"
            }

        return {
            "should_water": False,
            "confidence": 0.60,
            "method": "rule-based (optimal)"
        }


# ----------------------------------------------------------------------
# GLOBAL INSTANCE (used by API)
# ----------------------------------------------------------------------
predictor = GardenPredictor()
