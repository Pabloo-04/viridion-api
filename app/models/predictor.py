import pickle
import numpy as np
from pathlib import Path
from typing import Dict
from app.config import settings


class GardenPredictor:
    """ML model for garden predictions"""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or settings.model_path
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained model"""
        model_file = Path(self.model_path)
        
        if model_file.exists():
            with open(model_file, 'rb') as f:
                self.model = pickle.load(f)
            print(f"✅ Model loaded from {self.model_path}")
        else:
            print(f"⚠️  No trained model found at {self.model_path}")
            print("   Using rule-based predictions instead")
    
    def predict_watering(
        self, 
        temperature: float, 
        humidity: float, 
        soil_moisture: float, 
        hour: int
    ) -> Dict:
        """
        Predict if watering is needed
        
        Args:
            temperature: Temperature in Celsius
            humidity: Humidity percentage
            soil_moisture: Soil moisture percentage
            hour: Hour of day (0-23)
        
        Returns:
            Dict with should_water, confidence, and reasoning
        """
        
        # If model exists, use it
        if self.model is not None:
            try:
                features = np.array([[temperature, humidity, soil_moisture, hour]])
                prediction = self.model.predict(features)[0]
                confidence = self.model.predict_proba(features)[0].max()
                
                return {
                    "should_water": bool(prediction),
                    "confidence": float(confidence),
                    "reasoning": "ML model prediction"
                }
            except Exception as e:
                print(f"Model prediction failed: {e}")
                # Fall through to rule-based
        
        # Rule-based fallback
        should_water = False
        reasoning = []
        
        # Check soil moisture (primary factor)
        if soil_moisture < 30:
            should_water = True
            reasoning.append("Soil moisture critically low")
        elif soil_moisture < 40:
            # Check other conditions
            if temperature > 28:
                should_water = True
                reasoning.append("Low moisture + high temperature")
            elif humidity < 40:
                should_water = True
                reasoning.append("Low moisture + low humidity")
        
        # Avoid watering during hot midday (11-15h)
        if should_water and 11 <= hour <= 15:
            reasoning.append("(Best time: early morning or evening)")
        
        confidence = 0.85 if should_water and soil_moisture < 30 else 0.65
        
        return {
            "should_water": should_water,
            "confidence": confidence,
            "reasoning": " | ".join(reasoning) if reasoning else "Conditions optimal"
        }


# Initialize predictor
predictor = GardenPredictor()