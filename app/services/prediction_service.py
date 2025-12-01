from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.predictor import predictor
from app.database.database import Prediction, SensorReading
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from app.config import settings

class PredictionService:

    @staticmethod
    async def predict_and_save(db: AsyncSession, plant_id: str):
        """
        Fetch the latest sensor readings for a plant and make a prediction.
        """
        # Fetch the latest sensor reading for this plant
        stmt = (
            select(SensorReading)
            .where(SensorReading.plant_id == plant_id)
            .order_by(SensorReading.timestamp.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        latest_reading = result.scalar_one_or_none()

        if not latest_reading:
            raise HTTPException(
                status_code=404,
                detail=f"No sensor data found for plant_id: {plant_id}"
            )

        # Validate required fields
        if latest_reading.soil_moisture is None or latest_reading.humidity is None or latest_reading.temperature is None:
            raise HTTPException(
                status_code=400,
                detail=f"Incomplete sensor data for {plant_id}. Missing required fields (soil_moisture, humidity, or temperature)."
            )

        # Use ML model
        prediction_result = predictor.predict(
            soil_moisture=latest_reading.soil_moisture,
            soil_humidity=latest_reading.humidity,
            temperature=latest_reading.temperature
        )

        print("Soil Moisture: ", latest_reading.soil_moisture)
        print("Soil Humidity: ", latest_reading.humidity)
        print("Soil Temperature: " ,latest_reading.temperature)

        # Save prediction to DB
        new_record = Prediction(
            should_water=prediction_result["should_water"],
            confidence=prediction_result["confidence"],
            soil_moisture=latest_reading.soil_moisture,
            humidity=latest_reading.humidity,
            temperature=latest_reading.temperature,
            timestamp=datetime.now(ZoneInfo(settings.timezone))
        )
        db.add(new_record)
        await db.commit()
        await db.refresh(new_record)

        return new_record, prediction_result
