from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db, Prediction
from app.database.schemas import  PredictionResponse
from app.models.predictor import predictor
from datetime import datetime, timedelta

router = APIRouter()

"""""
@router.post("/watering", response_model=PredictionResponse)
async def predict_watering(data: PredictionRequest, db: Session = Depends(get_db)):
    Predict if garden needs watering using ML model
    
    # Get prediction from model
    result = predictor.predict_watering(
        data.temperature,
        data.humidity,
        data.soil_moisture,
        data.hour_of_day
    )
    
    # Store prediction in database
    prediction_record = Prediction(
        should_water=result["should_water"],
        confidence=result["confidence"],
        temperature=data.temperature,
        humidity=data.humidity,
        soil_moisture=data.soil_moisture,
        timestamp=datetime.utcnow()
    )
    db.add(prediction_record)
    db.commit()
    
    # Calculate next watering time
    if result["should_water"]:
        next_time = "Now"
    else:
        # Predict next check in 2-6 hours based on conditions
        hours_ahead = 2 if data.soil_moisture < 50 else 6
        next_time = (datetime.now() + timedelta(hours=hours_ahead)).strftime("%H:%M")
    
    return PredictionResponse(
        should_water=result["should_water"],
        confidence=result["confidence"],
        next_watering_time=next_time,
        reasoning=result.get("reasoning")
    )
"""

@router.get("/history")
async def get_prediction_history(limit: int = 100, db: Session = Depends(get_db)):
    """Get prediction history for analysis"""
    predictions = db.query(Prediction).order_by(
        Prediction.timestamp.desc()
    ).limit(limit).all()
    
    return [
        {
            "timestamp": pred.timestamp.isoformat(),
            "should_water": pred.should_water,
            "confidence": pred.confidence,
            "conditions": {
                "temperature": pred.temperature,
                "humidity": pred.humidity,
                "soil_moisture": pred.soil_moisture
            }
        }
        for pred in predictions
    ]