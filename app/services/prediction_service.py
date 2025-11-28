from sqlalchemy.orm import Session
from app.models.predictor import predictor
from app.database.database import Prediction
from datetime import datetime

class PredictionService:

    @staticmethod
    def predict_and_save(db: Session, soil_moisture: float, soil_humidity: float, temperature: float):
        
        # Use ML model
        result = predictor.predict(
            soil_moisture=soil_moisture,
            soil_humidity=soil_humidity,
            temperature=temperature
        )

        # Save to DB
        new_record = Prediction(
            should_water=result["should_water"],
            confidence=result["confidence"],
            soil_moisture=soil_moisture,
            humidity=soil_humidity,
            temperature=temperature,
            timestamp=datetime.utcnow()
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        return new_record, result
